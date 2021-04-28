from sklearn.cluster import KMeans
import numpy as np
from elasticsearch import Elasticsearch
import calc_er3


id_movies = calc_er3.id_movies_calc()
ratings=calc_er3.ratings_calc()
sum_movies=calc_er3.sum_of_movies(ratings,id_movies) #calculate the sum of the ratings the users gave for a movie
ratings=calc_er3.final_ratings(ratings,id_movies) #calculate the last ratings array
clusters_of_users=calc_er3.clustering_calc(ratings) #performe the clustering

#make an array of the clusters and the users in eache of them
cluster_to_user=[]
for x in range(max(clusters_of_users)+1):
    cluster_temp=[]
    for y in range(len(clusters_of_users)):
            if clusters_of_users[y]==x:
                cluster_temp.append(y)
    cluster_to_user.append(cluster_temp)

clusters_of_users=clusters_of_users.tolist()

#=====================================================================================================================================
# Adding a new useless comment here 

# connect to ElasticSearch
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

# change similarity to BM25
es.indices.close("movies")  # close the index
settings = {  # create similarity settings
    "index": {
        "similarity": {
            "default": {
                "type": "BM25"
            }
        }
    }
}
es.indices.put_settings(settings, "movies")  # change default similarity settings of index
es.indices.open("movies")  # open the index

while (1):  # loop for multiple searches

    # get search keyword from user
    keyword = input("\nEnter title keyword:\n")

    # get user id from user
    user_id = input("\nEnter user id:\n")

    # search using keyword in ElasticSearch (max results=10000)
    res = es.search(index='movies', size=10000, body={'query': {'match': {'title': keyword}}})

    # calculate max BM25 score of the results for normalisation
    all_BM25 = []
    for hit in res['hits']['hits']:
        all_BM25.append(hit['_score'])
    max_BM25 = max(all_BM25)
    print(max_BM25)

    # update similarity scores for each movie with custom metric
    # update similarity scores for each movie with custom metric
    for i in range(len(res['hits']['hits'])):
        hit = res['hits']['hits'][i]  # temporary variable for readability
        res['hits']['hits'][i]['_score'] = calc_er3.calc_metric(ratings,user_id, id_movies.index(res['hits']['hits'][i]['_id']),cluster_to_user,clusters_of_users,sum_movies,max_BM25,hit['_score'])  # calculate new metric using calc_metric.py



    # sort results based on updated metric in descending order
    res['hits']['hits'].sort(reverse=True, key=lambda x: x['_score'])

    # print all the results returned
    print("\nResults found: " + str(len(res['hits']['hits'])) + "\n")  # show number of results found
    print("id      " + "score   " + "movie")
    for hit in res['hits']['hits']:  # array res['hits']['hits'] contains all results
        output = '{:6}'.format(hit['_id']) + "\t" + '{:7}'.format(str(round(hit['_score'], 4))) + "\t" + hit['_source']['title'] + " [ "
        for genre in hit['_source']['genres']:
            output += genre + " "
        output += "]"
        print(output)  # print movie

    again = input("\nSearch again?(yes/no):\n")  # ask to search again

    while (again != 'yes' and again != 'no'):  # while inputmurder
        6489# is invalid
        again = input("\nPlease enter yes or no:\n")  # ask for input again

    if (again == 'no'):
        break  # if no get out of while loop
