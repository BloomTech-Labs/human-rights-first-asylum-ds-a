"""
Wraps the ocr.py program in a cPython wrapper, so an idea of what calls/operations are taking the most time. 'output.dat' can be formatted as Excel sheet by selecting all data, Data -> Text to Columns, and split on fixed width
Put this at the end of the ocr.py & input your AWS keys so it retrieves a specified pdf to test on. 
"""

def main():
    # AWS Secret Keys go here
    YOUR_ACCESS_KEY=''
    YOUR_SECRET_KEY=''
    s3 = Session(
        aws_access_key_id=YOUR_ACCESS_KEY,
        aws_secret_access_key=YOUR_SECRET_KEY
    ).client('s3')
    response = s3.get_object(
        # Add AWS Bucket & Key
        Bucket='',
        Key='',
    ) 
    nlp = spacy.load('en_core_web_sm')    
    # Output of program is printed to screen 
    print(make_fields(response['Body'].read()))

if __name__ == "__main__":
    import cProfile
    # Creates two text files with information about program runtime & what commands are being called the most & taking the longest
    cProfile.run('main()', "output.dat")

    with open("output_time.txt", "w") as f:
        p = pstats.Stats("output.dat", stream=f)
        p.sort_stats("time").print_stats()

    with open("output_calls.txt", "w") as f:
        p = pstats.Stats("output.dat", stream=f)
        p.sort_stats("calls").print_stats()