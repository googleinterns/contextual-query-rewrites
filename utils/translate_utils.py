from google.cloud import translate
import os
import threading
import json as Json
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def batch_translate_text(input_uri,
                         output_uri,
                         project_id,
                         src_lang="en",
                         dst_lang=["hi"]):
    """Batch translation of a file stored on GCS"""

    client = translate.TranslationServiceClient()

    location = "us-central1"
    gcs_source = {"input_uri": input_uri}

    input_configs_element = {
        "gcs_source": gcs_source,
        "mime_type": "text/plain"
    }

    gcs_destination = {"output_uri_prefix": output_uri}
    output_config = {"gcs_destination": gcs_destination}
    parent = client.location_path(project_id, location)

    operation = client.batch_translate_text(
        parent=parent,
        source_language_code=src_lang,
        target_language_codes=dst_lang,
        input_configs=[input_configs_element],
        output_config=output_config)

    print("Waiting for operation to complete...")
    response = operation.result()

    print(u"Total Characters: {}".format(response.total_characters))
    print(u"Translated Characters: {}".format(response.translated_characters))


def translate_text(line, src_lang, dst_lang, project_id):
    """
    Converts a line of text from src language to destination language
    """

    client = translate.TranslationServiceClient()
    parent = client.location_path(project_id, "global")

    response = client.translate_text(
        parent=parent,
        contents=[line],
        mime_type="text/plain",
        source_language_code=src_lang,
        target_language_code=dst_lang,
    )

    for translation in response.translations:
        print(u"Translated text: {}".format(translation.translated_text))
    return translation.translated_text


def batch_translate_file(input_path,
                         output_file,
                         gcs_bucket,
                         project_id,
                         src_lang="en",
                         dst_lang="hi",
                         threshold=20):
    """
    File is transferred to the GCS,
    gets translated and gets copied back
    """

    move_cmd = "gcloud storage cp {0} {1}".format(input_path,
                                             gcs_bucket + '/' + input_path)
    logging.info(move_cmd)
    os.system(move_cmd)

    batch_translate_text(gcs_bucket + '/' + input_path,
                         gcs_bucket + '/intermediate/', project_id)

    copy_back_cmd = "gcloud storage cp --recursive {0} {1}".format(gcs_bucket + '/intermediate/*.' \
                    + input_path.split('.')[1] + '/', output_file)
    logging.info("[EXECUTING] {0}".format(copy_back_cmd))
    os.system(copy_back_cmd)

    remove_intermediate_cmd = "gcloud storage rm --recursive --continue-on-error {0}".format(gcs_bucket +
                                                            '/intermediate')
    logging.info("[EXECUTING] {0}".format(remove_intermediate_cmd))
    os.system(remove_intermediate_cmd)

    logging.info("[WROTE] {0}".format(output_file))


def translate_data(input_path,
                   output_file,
                   config_file="config.json",
                   src_lang="en",
                   dst_lang="hi",
                   threshold=20):
    """
    translates data in the given input path.
    if the input_path is a directory, its individual files are translated

    files with greater than the number of elements specified in the threshold 
    are batch translated
    """

    with open(config_file) as json_file:
        config = Json.load(json_file)

    gcs_bucket = config["GCSBucket"]
    project_id = config["ProjectID"]

    if os.path.isdir(input_path):

        for file in os.listdir(input_path):
            batch_translate_file(os.path.join(input_path, file),
                                 './outputs/' + file, gcs_bucket, project_id,
                                 src_lang, dst_lang, threshold)

    else:
        file = open(input_path, 'r').readlines()

        if len(file) > threshold:
            batch_translate_file(input_path, output_file, gcs_bucket,
                                 project_id, src_lang, dst_lang, threshold)

        else:
            outfile = open(output_file, 'wb')

            for line in file:
                outfile.write(translate_text(line.strip(), src_lang, dst_lang, project_id).encode() \
                                 + '\n'.encode())

            outfile.close()
