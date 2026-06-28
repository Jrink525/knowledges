# Multi-modal message: text + image + structured data
multimodal_message = {
    "role": "user",
    "parts": [
        {"type": "text",
         "text": "Describe what is wrong with this chart and suggest fixes."},
        {"type": "file",
         "mimeType": "image/png",
         "bytes": base64.b64encode(chart_image_bytes).decode()},
        {"type": "data",
         "data": {
             "chartType": "bar",
             "dataSource": "Q3 Revenue by Region",
             "knownIssues": ["y-axis does not start at zero",
                             "missing error bars"]
         }}
    ]
}
\end{lstlisting}
\end{examplebox}

\begin{examplebox}[多模态 A2A 消息：图像分析]
\begin{lstlisting}[style=pythonstyle]
