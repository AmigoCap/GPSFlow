# coding UTF8

import distance

def fdistance(df, i, j) :
    return distance.haversineDistance(
        df["lng_mean_filt"][i],
        df["lat_mean_filt"][i],
        df["lng_mean_filt"][j],
        df["lat_mean_filt"][j])


def findStayPoints(df, lower_limit, radius, max_outliers) :
    is_mouvement = []
    segment_mouvement = []
    l = 0
    i = 0


    while i < (df["timestampMs"].size - max(lower_limit, max_outliers) - 1):
        # Vérifier si i est un début de stay point
        mouvement = False
        for k in range(lower_limit) :
            if (fdistance(df, i, i + k + 1) > radius) :
                mouvement = True

        if mouvement :
        # Si on est en mouvement, suivant
            if i > 0 :
                if not is_mouvement[i-1]:
                    l += 1
            i += 1
            is_mouvement.append(True)
            segment_mouvement.append(l)

        else :
            # Si on est immobile, trouver jusqu'à quel indice
            outliers = max_outliers
            l += 1

            #Debut du stay_point
            init_stay_point = i
            j = i + 1
            while outliers >= 0 and j < df["timestampMs"].size :
                if fdistance(df, i, j) > radius :
                    outliers -= 1

                else :
                    outliers = max_outliers
                j += 1

            i = j - max_outliers - 1
            # Fin du stay_point
            end_stay_point = i

            for m in range(init_stay_point,end_stay_point) :
                is_mouvement.append(False)
                segment_mouvement.append(l)

    if len(is_mouvement) < df["timestampMs"].size :
        if is_mouvement[i-1]:
            for n in range (i, df["timestampMs"].size) :
                is_mouvement.append(True)
                segment_mouvement.append(l)

        else :
            for n in range (i, df["timestampMs"].size) :
                is_mouvement.append(False)
                segment_mouvement.append(l)

    df["is_mouvement"] = is_mouvement
    df["segment_mouvement"] = segment_mouvement

    return df



