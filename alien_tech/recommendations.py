from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

def get_recommendations(user_id):
    user_courses = Enrollment.query.filter_by(user_id=user_id).all()
    all_courses = Course.query.all()
    
    user_course_descriptions = [course.description for course in user_courses]
    all_course_descriptions = [course.description for course in all_courses]
    
    tfidf = TfidfVectorizer().fit_transform(user_course_descriptions + all_course_descriptions)
    cosine_similarities = cosine_similarity(tfidf[:len(user_courses)], tfidf[len(user_courses):])
    
    similar_courses = sorted(list(enumerate(cosine_similarities.flatten())), key=lambda x: x[1], reverse=True)
    recommendations = [all_courses[i[0]] for i in similar_courses[:5]]
    return recommendations

@app.route('/recommendations', methods=['GET'])
@login_required
def recommendations():
    recommended_courses = get_recommendations(current_user.id)
    return render_template('recommendations.html', courses=recommended_courses)
