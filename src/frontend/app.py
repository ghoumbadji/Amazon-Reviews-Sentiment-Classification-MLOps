import gradio as gr
import requests
import os

API_URL = os.getenv("API_URL")

def analyze_sentiment(review_title, review_content):
    if not review_title or not review_content:
        return "**Please fill in both the title and the content.**", ""
    combined_text = f"{review_title} {review_content}"
    payload = {"content": combined_text}
    if not API_URL: 
        return "**API_URL not found in the environment.**"
    try:
        predict_url = f"{API_URL}/predict"
        response = requests.post(predict_url, json=payload)
        if response.status_code == 200:
            result = response.json()
            prediction = result.get("label", "Unknown")
            confidence = result.get("confidence", 0.0)
            sentiment_md = f"**Sentiment: {prediction.upper()}**"
            confidence_md = f"**Confidence Score: {confidence:.2%}**"
            return sentiment_md, confidence_md
        return f"**Error {response.status_code}**", response.text
    except requests.exceptions.ConnectionError:
        return "**Connection Error**", "Make sure the FastAPI backend is running."
    except Exception as e:
        return "**Unexpected Error**", str(e)


with gr.Blocks(title="Amazon Review Analyzer") as demo:
    gr.HTML("""
    <style>
        .limit-width { 
            max-width: 700px;
            margin-left: auto;
            margin-right: auto;
        }
        
        .center-text {
            text-align: center;
        }

        .custom-btn {
            background-color: #FF9900 !important; 
            color: black !important;
            font-weight: bold !important;
            border: 1px solid #e77600 !important;
        }
                
        .custom-btn:hover {
            background-color: #FA8900 !important;
        }
        
        .gradio-container label span {
            color: #232F3E !important;
            font-size: 1.1em !important;
            font-weight: 700 !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 5px;
            display: inline-block;
        }    
    </style>
    """)

    with gr.Column(elem_classes="limit-width"):
        gr.Markdown("\n\n")
        gr.Markdown(
            """
            # 🛒 **Amazon Review Sentiment Analysis**
            """,
            elem_classes="center-text"
        )
        gr.Markdown(
            "### Predict the sentiment of Amazon customer reviews using our **Inference API**",
            elem_classes="center-text"
        )
        gr.Markdown("---")
        # Inputs
        review_title = gr.Textbox(
            label="Review Title",
            placeholder="e.g. Great product but...",
            lines=1
        )
        review_content = gr.Textbox(
            label="Review Content",
            placeholder="e.g. I bought this item last week and I am very satisfied...",
            lines=5
        )
        analyze_btn = gr.Button("Analyze Review", elem_classes="custom-btn")
        gr.Markdown("---")
        with gr.Row():
            sentiment_output = gr.Markdown(label="Sentiment")
            confidence_output = gr.Markdown(label="Confidence")
        analyze_btn.click(
            fn=analyze_sentiment,
            inputs=[review_title, review_content],
            outputs=[sentiment_output, confidence_output]
        )


if __name__ == "__main__":
    demo.launch()