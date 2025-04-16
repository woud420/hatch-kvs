import pytest
import json
from src.model.response import Response

def test_success_response():
    response = Response("Ok", result="some value")
    expected_output = json.dumps({"status": "Ok", "result": "some value"})
    assert str(response) == expected_output

def test_error_response_with_message():
    response = Response("Error", mesg="Unexpected error!")
    expected_output = json.dumps({"status": "Error", "mesg": "Unexpected error!"})
    assert str(response) == expected_output

def test_success_response_without_result():
    response = Response("Ok")
    expected_output = json.dumps({"status": "Ok"})
    assert str(response) == expected_output

def test_error_response_without_message():
    response = Response("Error")
    expected_output = json.dumps({"status": "Error"})
    assert str(response) == expected_output

