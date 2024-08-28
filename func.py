import io
import json
import logging
import oci.auth.signers
import oci.generative_ai_inference
import os

from fdk import response

model_id = "cohere.command-r-plus"

try:
    endpoint = os.getenv("OCI_GENAI_ENDPOINT")
    compartment_id = os.getenv("COMPARTMENT_OCID")

    if not endpoint:
        raise ValueError("ERROR: Missing configuration key OCI_GENAI_ENDPOINT")
    if not compartment_id:
        raise ValueError("ERROR: Missing configuration key COMPARTMENT_OCID")

    signer = oci.auth.signers.get_resource_principals_signer()
    generative_ai_inference_client = oci.generative_ai_inference.GenerativeAiInferenceClient(config={}, service_endpoint=endpoint, signer=signer,retry_strategy=oci.retry.NoneRetryStrategy(), timeout=(10,240))
except Exception as e:
   logging.getLogger().error(e)
   raise

def inference(message):
    chat_request = oci.generative_ai_inference.models.CohereChatRequest()
    chat_request.message = f'''
    ##あなたは翻訳の専門家です。与えられた原文が日本語かどうかを判断して以下の指示のとおりに翻訳することが仕事です。
    ##以下の文章は翻訳対象の原文です。
    ##原文：{message}
    ##指示：以下のSTEPに従って原文を翻訳してください。
    ###STEP-1：原文が主に日本語であるかどうかを判断します。
    ###STEP-2：原文が主に日本語の場合は英語に翻訳します。
    ###STEP-3：原文が主に日本語以外の場合は日本語に翻訳します。
    ###STEP-4：以下の出力フォーマットに従って出力します。途中のSTEPの結果は出力しません。
    ##出力フォーマット：{{"input": "原文","output": "翻訳文"}}
    ##以下は原文とそれに対するあなたの出力の例です。
    ###Example-1：原文：こんにちは！
    出力：{{"input": "こんにちは！","output": "Hello!"}}
    ###Example-2：原文：Good morning.
    出力：{{"input": "Good morning.","output": "おはようございます。"}}
    '''
    chat_request.max_tokens = 2000
    chat_request.is_stream = False
    chat_request.temperature = 0.0
    chat_request.top_p = 0.7
    chat_request.top_k = 0 # Only support topK within [0, 500]
    chat_request.frequency_penalty = 1.0
    chat_request.is_echo = False

    chat_detail = oci.generative_ai_inference.models.ChatDetails()
    chat_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(model_id=model_id)
    chat_detail.compartment_id = compartment_id
    chat_detail.chat_request = chat_request

    try:
        chat_response = generative_ai_inference_client.chat(chat_detail)
        return chat_response.data.chat_response.text
    except Exception as e:
        logging.getLogger().error(e)
        raise

def handler(ctx, data: io.BytesIO = None):
    message = "こんにちは！"
    try:
        body = json.loads(data.getvalue())
        message = body["message"]
    except (Exception, ValueError) as ex:
        logging.getLogger().info('error parsing json payload: ' + str(ex))     
    logging.getLogger().info("Inside Python Hello World function")

    inference_response  = inference(message)

    return response.Response(
        ctx, response_data=json.dumps(
            {"message": "{0}".format(inference_response)},
            ensure_ascii=False
        ),
        headers={"Content-Type": "application/json; charset=utf-8"}
    )
