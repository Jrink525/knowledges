# 加载任意OpenAPI 3.x规范——可以是本地文件或获取的URL
spec = """
openapi: "3.0.3"
info:
  title: Weather API
  version: "1.0"
paths:
  /forecast:
    get:
      operationId: get_forecast
      summary: Get weather forecast for a location
      parameters:
        - name: city
          in: query
          required: true
          schema: {type: string}
        - name: days
          in: query
          schema: {type: integer, default: 3}
      responses:
        '200':
          description: Forecast data
"""

