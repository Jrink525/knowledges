# A message combining text instructions with a data payload and a file
message = {
    "role": "user",
    "parts": [
        {
            "type": "text",
            "text": "Analyze the attached CSV and the schema below. "
                    "Identify anomalies and produce a summary report."
        },
        {
            "type": "file",
            "mimeType": "text/csv",
            "uri": "https://storage.example.com/data/sales_q3.csv"
        },
        {
            "type": "data",
            "data": {
                "schema": {
                    "columns": ["date", "region", "product", "revenue", "units"],
                    "types":   ["date", "string", "string", "float", "int"]
                },
                "expectedRowCount": 15000,
                "anomalyThreshold": 3.0  # z-score threshold
            }
        }
    ]
}
\end{lstlisting}
\end{examplebox}

\begin{examplebox}[多模态 A2A 消息：数据分析]
\begin{lstlisting}[style=pythonstyle]
