from sklearn.cluster import KMeans
import numpy as np

#----------------------------------------------------------------------------

def id_movies_calc():
    # find the ids of the movies
    file = open('movies.csv', 'r', encoding='utf-8')
    file.readline()  # skip first line
    line = file.readline()  # save line into variable
    id_movies = []
    while line:  # from each line (each rating)
        line = line.split(',')
        id_movies.append(line[0])
        # go to next line
        line = file.readline()
    file.close()

    return id_movies

#----------------------------------------------------------------------------

def num_lines_calc():
    # get the mumber of movies and the number of users
    file = open('movies.csv', 'r', encoding='utf-8')
    lines = file.readlines()
    last_line = lines[-1].split(',')
    num_lines = int(last_line[0])
    file.close()

    return num_lines

#----------------------------------------------------------------------------

def ratings_calc():

    num_rat = sum(1 for line in open('ratings.csv', 'r', encoding='utf-8'))
    num_lines = num_lines_calc()

    ratings = []
    rating = [0.0] * (num_lines + 1)

    # create an array with rows being the users and columns being the movies and record the ratings there
    file = open('ratings.csv', 'r', encoding='utf-8')
    file.readline()  # skip first line
    line = file.readline()  # save line into variable
    user_count = 1
    line_counter = 0
    while line:  # from each line (each rating)
        line_counter = line_counter + 1
        line = line.rstrip()  # first remove trailling spaces and new line character
        line = line.split(",")
        if int(line[0]) == user_count:
            rating[int(line[1])] = float(line[2])
        else:
            ratings.append(rating)  # put rating in ratings list
            user_count = user_count + 1
            rating = [0] * (num_lines + 1)
            rating[int(line[1])] = float(line[2])

        if num_rat == line_counter + 1:
            ratings.append(rating)  # put rating in ratings list
        # go to next line
        line = file.readline()
    file.close()

    return ratings

#----------------------------------------------------------------------------

def sum_of_movies(ratings,id_movies):
    # calculate the sum of the ratings of all teh movies
    num_lines = num_lines_calc()
    sum_col2 = [0.0] * (num_lines + 1)
    sum_col = [sum(x) for x in zip(*ratings)]

    for x in range(len(ratings)):
        for y in id_movies:
            if ratings[x][int(y)]:
                sum_col2[int(y)] = sum_col2[int(y)] + 1
    # calculate the MESO ORO of the ratings of every movie
    # (only for the users that voted)
    sum_col3 = []
    for x in id_movies:
        if sum_col2[int(x)] != 0:
            sum_col3.append(sum_col[int(x)] / sum_col2[int(x)])
        else:
            sum_col3.append(0)

    return sum_col3

#----------------------------------------------------------------------------

def final_ratings(ratings,id_movies):
    ratings2 = []
    for x in range(len(ratings)):
        only_ratings = []
        for y in id_movies:
            only_ratings.append(ratings[x][int(y)])
        ratings2.append(only_ratings)
    return ratings2

#----------------------------------------------------------------------------

def clustering_calc(ratings):
    # create the numpy array and normalize the data
    ratings = np.asarray(ratings)

    # compute the clustrering  for the data
    # AffinityPropagation
    clustering = KMeans(n_clusters=8, tol=0.00001).fit(ratings)
    # and find out in wich cluster every user belongs
    clusters_of_users = clustering.predict(ratings)

    return clusters_of_users

#----------------------------------------------------------------------------

def calc_metric(ratings,user_id,mo_id,cluster_to_user,clusters_of_users,sum_movies,max_BM25,score):


    sum_rating = 0
    num_sum = 0
    sum_cluster=0
    user_id = int(user_id)
   # if ratings[user_id - 1][mo_id] == 0:
    for x in cluster_to_user[clusters_of_users[user_id - 1]]:
        sum_rating = sum_rating + ratings[x][mo_id]
        num_sum = num_sum + 1
    if    num_sum != 0:
        sum_cluster=sum_rating/num_sum
    if ratings[user_id - 1][mo_id] == 0:
        if sum_rating != 0:
            ratings[x][mo_id] = sum_rating / num_sum
        else:
            ratings[x][mo_id] = sum_movies[mo_id]
    ratings[user_id - 1][mo_id] = ratings[user_id - 1][mo_id] / 5
    return (score / max_BM25) * 0.5 + (ratings[user_id - 1][mo_id]/5) * 0.3 + sum_cluster * 0.2 #+ (sum_movies[mo_id]/5) * 0.2