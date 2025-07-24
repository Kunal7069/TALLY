from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route('/get-companies', methods=['GET'])
def get_companies():
    xml_request = """
    <ENVELOPE>
        <HEADER>
            <TALLYREQUEST>Export Data</TALLYREQUEST>
        </HEADER>
        <BODY>
            <EXPORTDATA>
                <REQUESTDESC>
                    <REPORTNAME>List of Companies</REPORTNAME>
                </REQUESTDESC>
            </EXPORTDATA>
        </BODY>
    </ENVELOPE>
    """

    try:
        response = requests.post("http://192.168.215.57:9000", data=xml_request, headers={"Content-Type": "application/xml"})
        response.raise_for_status()
        return response.text, 200, {'Content-Type': 'application/xml'}

    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
