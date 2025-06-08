from crewai_tools import FileWriterTool
import os

# --- Test Configuration ---
TEST_DIRECTORY = "test_output_dir"
TEST_FILENAME = "test_output.txt"
TEST_CONTENT = "Hello from the FileWriterTool test!\nThis is a test line.\nAnother line of test content."
# -------------------------

def test_file_writer():
    """Tests the FileWriterTool from crewai_tools."""
    print(f"Attempting to write a test file using FileWriterTool...")

    # Initialize the tool
    file_writer = FileWriterTool()

    # Define the full path for the test directory
    # Assuming the script is run from the project root or a known location
    # For simplicity, creating it in the current working directory
    # If your project root is /Users/satyamsinghal/Desktop/Products/AIA_Interface,
    # this will create /Users/satyamsinghal/Desktop/Products/AIA_Interface/test_output_dir
    output_dir_path = os.path.join(os.getcwd(), TEST_DIRECTORY)

    print(f"Target directory: {output_dir_path}")
    print(f"Target filename: {TEST_FILENAME}")
    print(f"Content to write:\n{TEST_CONTENT}\n")

    try:
        # Write content to a file in the specified directory
        # The _run method expects: filename, content, directory
        # The tool's _run method might expect a dictionary of arguments,
        # especially when called by an agent. The error suggested an 'overwrite' key.
        # We are inferring 'file_path' and 'text' as other likely keys.
        args_dict = {
            'file_path': os.path.join(output_dir_path, TEST_FILENAME),
            'text': TEST_CONTENT,
            'overwrite': True
        }
        print(f"Calling _run with args: {args_dict}")
        result = file_writer._run(**args_dict)
        print(f"FileWriterTool execution result: {result}")

        # Verification step
        expected_file_path = os.path.join(output_dir_path, TEST_FILENAME)
        if os.path.exists(expected_file_path):
            print(f"SUCCESS: File '{expected_file_path}' was created.")
            with open(expected_file_path, 'r', encoding='utf-8') as f:
                written_content = f.read()
            if written_content == TEST_CONTENT:
                print("SUCCESS: File content matches the expected content.")
            else:
                print("ERROR: File content does NOT match the expected content.")
                print(f"Expected:\n{TEST_CONTENT}")
                print(f"Got:\n{written_content}")
        else:
            print(f"ERROR: File '{expected_file_path}' was NOT created.")

    except Exception as e:
        print(f"An error occurred during the test: {e}")

if __name__ == "__main__":
    test_file_writer()
