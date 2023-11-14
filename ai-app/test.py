import argparse

def main():
    parser = argparse.ArgumentParser(description= '''Collect jobs data and train a ChatBot on it and creates you a Streamlit
                                                     app to ask the ChatBot for jobs that fits you (FOR FREE !!!!) ''')

    parser.add_argument('--country',   type= str, required= True, help= 'Specify a valid country name or a geographic region.')
    parser.add_argument('--job_title', type= str, required= True, help= 'Specify a job title to search for as a string.')

    args = parser.parse_args()

    country   :str = args.hello
    job_title :str = args.hello

    # Your code here
    print(f"Hello, {country}!")

if __name__ == '__main__':
    main()
