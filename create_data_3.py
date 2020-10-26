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

new_ratings=[]
for x in range(len(cluster_to_user)):
    users = cluster_to_user[x]
    temp_ratings = []
    for y in range(len(id_movies)):
        sum_rating = 0
        num_sum = 0
        for z in users:
            if ratings[z][y] != 0:
                sum_rating = sum_rating + ratings[z][y]
                num_sum = num_sum + 1
        if num_sum != 0:
            temp_ratings.append(sum_rating/num_sum)
        else:
            temp_ratings.append(sum_movies[y])

    new_ratings.append(temp_ratings)


for x in range(len(ratings)):
    for y in range(len(id_movies)):
        if ratings[x][y]==0:
            ratings[x][y]= new_ratings[clusters_of_users[x]][y]


f = open("new_cluster_ratings.csv", "w")
for x in range(len(ratings)):
    for y in range(len(id_movies)):
        line= str(x+1) + ',' + str(id_movies[y]) + ',' +  str(ratings[x][y]) + '\n'
        f.write(line)
f.close()
