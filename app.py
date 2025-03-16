#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gradio as gr
import os
from main import translate_markdown
from markdown_to_html import convert_markdown_to_html_string

def translate_text(
    input_text, 
    lang_in, 
    lang_out, 
    service, 
    model=None, 
    api_key=None, 
    ignore_cache=False
):
    """
    Translate the input text using the selected translation service
    """
    # If API key is provided in the UI, use it; otherwise, it will use the one from .env
    api_key = api_key if api_key and api_key.strip() else None
    
    # Call the translate_markdown function from main.py
    translated_text = translate_markdown(
        markdown_text=input_text,
        lang_in=lang_in,
        lang_out=lang_out,
        service=service,
        model=model,
        api_key=api_key,
        ignore_cache=ignore_cache
    )
    
    return translated_text

# Function to convert language display name to code
def get_lang_code(lang_name):
    lang_map = {
        "英语": "en",
        "中文": "zh",
        "日语": "ja",
        "韩语": "ko",
        "法语": "fr",
        "德语": "de",
        "西班牙语": "es",
        "意大利语": "it",
        "俄语": "ru",
        "葡萄牙语": "pt"
    }
    return lang_map.get(lang_name, "en")

# Function to load Markdown file
def load_markdown_file(file_obj):
    if file_obj is None:
        return None
    content = file_obj.decode("utf-8")
    return content

# Function to convert Markdown to HTML
def render_markdown(markdown_text):
    if not markdown_text:
        return ""
    html_content = convert_markdown_to_html_string(markdown_text)
    return html_content

# Create the Gradio interface
with gr.Blocks(title="Markdown Bridge - 翻译工具") as app:
    gr.Markdown("# Markdown Bridge 📝 ↔️ 🌐")
    gr.Markdown("一个强大的 Markdown 文档翻译工具，支持保留 LaTeX 公式、代码块、图片链接等特殊元素")
    
    with gr.Row():
        with gr.Column():
            # Add file upload button for Markdown files
            file_upload = gr.File(
                label="上传 Markdown 文件",
                file_types=[".md", ".markdown", ".txt"],
                type="binary"
            )
            
            # Input section with both raw text and rendered preview
            with gr.Tabs():
                with gr.TabItem("编辑"):
                    input_text = gr.Textbox(
                        label="输入 Markdown 文本",
                        placeholder="在此输入要翻译的 Markdown 文本或上传 Markdown 文件...",
                        lines=15
                    )
                
                with gr.TabItem("预览"):
                    input_preview = gr.HTML()
            
            with gr.Row():
                lang_in = gr.Dropdown(
                    choices=["英语", "中文", "日语", "韩语", "法语", "德语", "西班牙语", "意大利语", "俄语", "葡萄牙语"],
                    value="英语",
                    label="源语言"
                )
                
                lang_out = gr.Dropdown(
                    choices=["英语", "中文", "日语", "韩语", "法语", "德语", "西班牙语", "意大利语", "俄语", "葡萄牙语"],
                    value="中文",
                    label="目标语言"
                )
            
            with gr.Row():
                service = gr.Radio(
                    choices=["google", "deepl", "openai", "deepseek"],
                    value="google",
                    label="翻译服务"
                )
                
                model = gr.Textbox(
                    label="模型名称 (仅 OpenAI 和 DeepSeek)",
                    placeholder="例如: gpt-3.5-turbo",
                    visible=False
                )
            
            with gr.Row():
                api_key = gr.Textbox(
                    label="API 密钥 (仅 DeepL、OpenAI 和 DeepSeek)",
                    placeholder="如果已在 .env 文件中配置，可留空",
                    visible=False,
                    type="password"
                )
                
                ignore_cache = gr.Checkbox(
                    label="忽略缓存",
                    value=False
                )
            
            # Add translate button
            translate_btn = gr.Button("翻译", variant="primary")
        
        with gr.Column():
            # Output section with both raw text and rendered preview
            with gr.Tabs():
                with gr.TabItem("文本"):
                    output_text = gr.Textbox(
                        label="翻译结果",
                        lines=15,
                        interactive=False
                    )
                
                with gr.TabItem("预览"):
                    output_preview = gr.HTML()
    
    # Connect file upload to input text
    file_upload.change(
        fn=load_markdown_file,
        inputs=file_upload,
        outputs=input_text
    )
    
    # Update input preview when input text changes
    input_text.change(
        fn=render_markdown,
        inputs=input_text,
        outputs=input_preview
    )
    
    # Add examples with proper formatting
    examples = gr.Examples(
        examples=[
            [
                "# Introduction\n\nThis is a sample Markdown text with a LaTeX formula: $E=mc^2$.\n\n```python\nprint('Hello, world!')\n```\n\n![Sample Image](https://example.com/image.jpg)",
            ],
            [
                "# Abstract\n\nIn this paper, we propose a novel approach to $f(x) = \\sum_{i=1}^{n} x_i^2$ optimization.",
            ]
        ],
        inputs=[input_text],
    )
    
    # Define function to update UI based on selected service
    def update_ui(service_value):
        if service_value in ["openai", "deepseek"]:
            return gr.update(visible=True), gr.update(visible=True)
        elif service_value == "deepl":
            return gr.update(visible=False), gr.update(visible=True)
        else:  # google
            return gr.update(visible=False), gr.update(visible=False)
    
    # Connect the translate button to the translate function
    def on_translate_click(text, src_lang, tgt_lang, svc, mdl, key, cache):
        src_code = get_lang_code(src_lang)
        tgt_code = get_lang_code(tgt_lang)
        translated = translate_text(text, src_code, tgt_code, svc, mdl, key, cache)
        html_content = render_markdown(translated)
        return translated, html_content
    
    translate_btn.click(
        fn=on_translate_click,
        inputs=[
            input_text,
            lang_in,
            lang_out,
            service,
            model,
            api_key,
            ignore_cache
        ],
        outputs=[output_text, output_preview]
    )
    
    # Update UI when service is changed
    service.change(
        fn=update_ui,
        inputs=service,
        outputs=[model, api_key]
    )
    
    # Also update input preview when examples are clicked
    examples.dataset.click(
        fn=lambda x: (x, render_markdown(x)),
        inputs=[input_text],
        outputs=[input_text, input_preview]
    )

if __name__ == "__main__":
    # Launch the interface
    app.launch(share=False)
