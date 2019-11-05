import statistics
from csv import reader
import math
import csv 
import sys
import ast
from ast import literal_eval


def ReadFile(filename):
    ratings_counter = 0
    users = {}
    item_ratings = {}
    user_ratings = {}                                               
    with open(filename, "r") as csvfile:
        read = csv.reader(csvfile, delimiter='\t')
        for line in read:                                           
            user_id = int(line[0])
            item_id = int(line[1])
            rating_val = int(line[2])
            if user_id not in user_ratings.keys():                  
                user_ratings[user_id] = {}
            if item_id not in item_ratings.keys():                  
                item_ratings[item_id] = {}
            user_ratings[user_id].update({item_id: rating_val})
            item_ratings[item_id].update({user_id: rating_val})     
            ratings_counter += 1
    csvfile.close()
    return item_ratings, users, ratings_counter



def UserInfo(users):
    for user,user_list in users.items():
        user_ratings = user_list.ratings.values()
        user_list.mean = statistics.mean(user_ratings)
        user_list.median = statistics.median(user_ratings)
        user_list.min = min(user_ratings)
        user_list.max = max(user_ratings)

        if len(user_ratings) > 1:
            user_list.rating.standartdev = statistics.stdev(user_ratings)
            user_list.neighbors = []
    return users




def CosineSimilarity(users,user_1,user_2,min_correlation):
    try:
        user1 = users[user_1]
        user2 = users[user_2]
    except KeyError:
        return 0

    correlated = set(user_1.ratings.keys()).intersection(user_2.ratings.keys())

    if len(correlated) < min_correlation:
        return 0

    else:
        numerator1 = []
        numerator2 = []
        A = 0
        B = 0

        for i in correlated:
            numerator1.append(user1.ratings[item])
            numerator2.append(user2.ratings[item])

            A += pow(user1.ratings[item], 2)
            B += pow(user2.ratings[item], 2)

            numerator = sum(user1_info * user2_info for user1_info, user2_info in zip(numerator1,numerator2))
            A = math.sqrt(A)
            B = math.sqrt(B)
            denominator = A * B
            similarity = numerator/denominator

            return similarity


def Range(x):
    cosMin = 0
    PearsonMin = -1
    cosMax = 1
    PearsonMax = 1
    COS = cosMax - cosMin
    PEARSON = PearsonMax - PearsonMin
    return ((( x - cosMin ) * PEARSON ) / COS) + PearsonMin



def UserSimilarity(users):
    print("Calculating similarity...")
    similarity = []
    user_similarity = {}
    for user1 in ast.literal_eval(users).keys():
        for user2 in ast.literal_eval(users).keys():
            if user1 != user2:
                if user1 < user2:
                    if user1 not in user_similarity.keys():
                        user_similarity[user1] = {}
                    similarity_value = CosineSimilarity(users,user1,user2)
                    user_similarity[user1][user2] = similarity_value
                else:
                    if user2 not in user_similarity.keys():
                        user_similarity[user2] = {}
                    similarity_value = CosineSimilarity(users,user1,user2)
                    user_similarity[user2][user1] = similarity_value
                similarity.append(similarity_value)
    return similarity



def NearestNeighbors(users,user_similarity,k):
    for user_id,user in users.items():
        neighbors = {}
        if user_id in user_similarity.keys():
            for i,similarity in user_similarity[user_id].items():
                neighbors[i] = similarity
                for user1,similarity in user_similarity.items():
                    for user2,rating in similarity.items():
                        if user_id == user2:
                            neighbors[user1] = rating


    neighbors = sorted(neighbors.items(), key=lambda x:x[1], reverse=True)
    if len(neighbors) < k:
        limit = len(neighbors)
    else:
        limit = k

    for i in range (0,limit):
        i_id = neighbors[i][0]
        i_similarity = neighbors[i][1]
        user.neighbors.append(i_id)
    return



def Prediction(users,user_id,item_id,user_similarity):
    user = user[user_id]
    numerator = 0
    denominator = 0
    if user.neighbors == []:
        return None

    for n in user.neighbors:
        if item_id in users[n].ratings.keys():
            if user_id < n:
                numerator += ((users[n].ratings[item_id] - users[n].rating_mean) * Range(user_similarity[user_id][n]))
                denominator += abs(Range(user_similarity[user_id][n]))
            else:
                numerator += ((users[n].ratings[item_id] - users[n].rating_mean) * Range(user_similarity[n][user_id]))
                denominator += abs(Range(user_similarity[n][user_id]))

    if denominator == 0:                                                    
        return None

    prediction = user.rating_mean + numerator/float(denominator)            
    return prediction



def Recommender(users,item_ratings,ratings_counter):
    print("Recommending..")
    prediction_counter = 0

    with open('results.txt', "w") as csvfile:
        results_printer = csv.writer(csvfile, delimiter=',')
        for user,user_ratings in ast.literal_eval(users).items():
            for item in item_ratings.keys():
                recommendations = Prediction(users,user,item,item_ratings)

                if recommendations is not None:
                    prediction_counter += 1
                    if item in user_ratings.ratings.keys():
                        results_printer.writerow([user, item, actual_rating, predicted_rating])

        csvfile.close()



if __name__ == "__main__" :

    if len(sys.argv)<2:
        print ("Fatal: You forgot to include the directory name on the command line.")
        print ("Usage:  python %s <directoryname>" % sys.argv[0])
        sys.exit(1)

training_set = str(sys.argv[1])
testing_set = str(sys.argv[2])

ratings_train = ReadFile(training_set)
ratings_test = ReadFile(testing_set)


users,item_ratings,ratings_counter = ReadFile(training_set)

similarity = UserSimilarity(users)
recommendations = Recommender(users,item_ratings,ratings_counter)

print(recommendations)


