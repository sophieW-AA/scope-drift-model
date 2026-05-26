import warnings
warnings.filterwarnings('ignore',message='.*credentials from Google Cloud SDK.*',append=True)
warnings.filterwarnings('ignore',message='.*All-NaN axis encountered.*',append=True)

import pandas as pd
import numpy as np
from google.cloud import bigquery
import datetime as dt

import os
from openai import OpenAI

from ast import literal_eval

import regex as re

TOP_FIELD = 'medicine'

API_KEY = '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'


def main():

    client = bigquery.Client(project='ocean-tech-adv-analytics-c-esf')
    query_job = client.query('SELECT * FROM fsefos_medicine.term_gen_pub_list')
    results = query_job.result()
    df_pubs_list = results.to_dataframe()

    client = bigquery.Client(project='ocean-tech-adv-analytics-c-esf')
    query_job = client.query('SELECT * FROM fsefos_medicine.term_gen_output_l1')
    results = query_job.result()
    df_output_l1 = results.to_dataframe()

    try:
        client = bigquery.Client(project='ocean-tech-adv-analytics-c-esf')
        query_job = client.query('SELECT * FROM fsefos_medicine.term_gen_output_l2')
        results = query_job.result()
        df_output_l2 = results.to_dataframe()
        reviewed = list(df_output_l2.pub_id.unique())
    except:
        reviewed = []

    client = bigquery.Client(project='ocean-tech-adv-analytics-c-esf')
    query_job = client.query('SELECT * FROM fsefos_medicine.term_gen_fields_iter3')
    results = query_job.result()
    df_fos = results.to_dataframe()

    df_pubs_list = pd.merge(df_pubs_list,df_output_l1[pd.notnull(df_output_l1.key_term)][['pub_id']].drop_duplicates().rename(columns={'pub_id':'PublicationId'}))

    pubs_list = [x for x in df_pubs_list.PublicationId.to_list() if x not in reviewed]

    for n,pub_id in enumerate(pubs_list):

        n_plus = n + len(reviewed)

        try:

            output_dict = {}
            output_dict[pub_id] = {}

            print('{} {}'.format(n_plus,pub_id))

            for fos_l1 in df_output_l1[df_output_l1.pub_id==pub_id].fos.unique():

                print(' {} {}'.format(fos_l1,dt.datetime.now().strftime('%Y%m%d %H:%M:%S')))

                fos = '\n'.join(df_fos[df_fos.field_1.str.lower()==fos_l1].field_2.drop_duplicates().to_list())

                prompt = '''
                Here is an article title & abstract in the field of {top_field}, subfield {fos_l1}:
                {title}
                {abstract}

                Here is a list of fields of study within subfield {fos_l1}:
                {fos}

                Return only the fields of study from the above list that this article is strongly associated with along with the terms that associate the article with the field.
                A term is a word or a few words, not a whole clause or sentence.
                Fields of study that do not exist in the above list should not be considered or included in the output.

                Output should be formatted as a python dictionary where the keys are the fields of study and the values are a python list of the associated terms.
                The output should just be the dictionary, with no explanation.

                If this article does not fall into the general field of {top_field} then return blank.
                '''

                title = df_pubs_list[df_pubs_list.PublicationId==pub_id].iloc[0].Title
                abstract = df_pubs_list[df_pubs_list.PublicationId==pub_id].iloc[0].Abstract

                format_dict = {'top_field':TOP_FIELD,
                               'fos_l1':fos_l1,
                               'title':title,
                               'abstract':abstract,
                               'fos':fos}

                client = OpenAI(api_key=API_KEY)
                chat_completion  = client.chat.completions.create(model="gpt-5",
                                                                  messages=[{'role':'user',
                                                                             'content':prompt.format(**format_dict)}])

                print('  gpt cats returned {}'.format(dt.datetime.now().strftime('%Y%m%d %H:%M:%S')))

                try:
                    chat_response = literal_eval(chat_completion.choices[0].message.content)
                    output_dict[pub_id][fos_l1] = chat_response
                except:
                    output_dict[pub_id][fos_l1] = {'xxxxxxx no term xxxxxxx':['']}

            df_output = pd.DataFrame([[k,k1.lower(),k2.lower(),x] for k,v in output_dict.items() for k1,v1 in v.items() for k2,v2 in v1.items() for x in v2],columns=['pub_id','parent_fos','fos','key_term'])

            job_config = bigquery.LoadJobConfig()
            client = bigquery.Client(project='ocean-pub-market-intell-s-dit')
            job = client.load_table_from_dataframe(df_output,
                                                   'data_analytics.term_gen_output_l2',
                                                   job_config=job_config)

        except:
            print('  error')
            pass


if __name__ == "__main__":
    main()