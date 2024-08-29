import gradio as gr
import requests
import json
import re

def translate(text):
    url = "エンドポイント名/v1/translate"
    headers = {"Content-Type": "application/json"}
    data = {"message": text}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        result = response.json()
        message = result["message"]
        
        # JSONデータを抽出し、改行をエスケープ
        json_match = re.search(r'\{.*\}', message, re.DOTALL)
        if json_match:
            try:
                json_string = json_match.group().replace('\n', '\\n')
                json_data = json.loads(json_string)
                return json_data.get("output", message)
            except json.JSONDecodeError:
                return message
        else:
            return message
    except requests.exceptions.RequestException as e:
        return f"エラーが発生しました: {str(e)}"

with gr.Blocks() as demo:
    gr.Markdown("# とにかく翻訳する青山アイさん")
    
    with gr.Row():
        input_text = gr.Textbox(label="翻訳したい文章", lines=5, scale=1, show_copy_button=True)
        translate_button = gr.Button("翻訳", scale=0, min_width=100)
        output_text = gr.Textbox(label="翻訳結果", lines=5, scale=1, show_copy_button=True)
    with gr.Row():
        clear_button = gr.ClearButton(components=[input_text], value="クリア")

    translate_button.click(fn=translate, inputs=input_text, outputs=output_text)

demo.launch(share=True)