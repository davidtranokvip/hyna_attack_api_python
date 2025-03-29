# Flask API Documentation

## Introduction
This is a simple Flask-based API for checking HTTP response status from multiple locations using [Check-Host](https://check-host.net/).

## Installation

### Prerequisites
- Python 3.x
- `pip` (Python package manager)

### Setup
1. Clone this repository:
   ```sh
   git clone https://github.com/your-repo/flask-api.git
   cd flask-api
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage

### Start the server
Run the Flask application:
```sh
python app.py
```
The API will start on `http://127.0.0.1:5000/` by default.

### Endpoints
#### 1. **Check HTTP Status**
- **URL:** `/check`
- **Method:** `POST`
- **Content-Type:** `application/json`
- **Request Body:**
  ```json
  {
    "host": "example.com",
    "max_nodes": 5
  }
  ```
- **Response Example:**
  ```json
  {
    "ip": "104.21.9.235",
    "country": "Brazil",
    "capital_city": "Sao Paulo",
    "statusCode": "200",
    "statusText": "OK"
  }
  ```

### Error Handling
| Error | Message |
|--------|--------------------------------|
| 400 | Missing 'host' parameter in JSON. |
| 500 | Unable to send check request. |
| 500 | Failed to receive request_id. |
| 500 | Unable to fetch check results. |

## License
This project is licensed under the MIT License.
