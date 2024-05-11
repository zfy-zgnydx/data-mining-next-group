import pandas as pd
import matplotlib.pyplot as plt
import sys
import re
from nltk.corpus import stopwords
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics.pairwise import cosine_similarity
import os


def clean_text(text):
    # 统一小写
    text = text.lower()
    # 删除标点符号和特殊字符
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    # 删除停止语
    stop_words = set(stopwords.words('english'))
    # 将文本拆分为多个单词，不带停止语
    text = ' '.join([word for word in text.split() if word not in stop_words])
    return text


def sentiment_analysis(text):
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0.1:
        return 'Positive'
    elif analysis.sentiment.polarity < -0.1:
        return 'Negative'
    else:
        return 'Neutral'


def hybrid_recommendation(product_id, content_sim_matrix, product_user_matrix, products, top_n=10):
    # Get the index of the product that matches the product_id
    idx = products.index[products['product_id'] == product_id][0]
    #print(idx)
    # 基于文本推荐
    # 根据相似度得分获取top_n
    sim_scores = list(enumerate(content_sim_matrix[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    content_recommendations_idx = [i[0] for i in sim_scores[1:top_n + 1]]
    # print("文本推荐结果：")
    #print(content_recommendations_idx)
    # 基于协同过滤的推荐
    # 获取当前产品得分
    if product_id in product_user_matrix.index:
        current_product_rating = product_user_matrix.loc[product_id].values[0]
        # 查询分数相近的相似产品
        similar_rating_products = product_user_matrix.iloc[
            (product_user_matrix['rating'] - current_product_rating).abs().argsort()[:top_n]]

    # 索引并构建map
    collaborative_recommendations_idx = similar_rating_products.index
    collaborative_recommendations_idx = [products.index[products['product_id'] == pid].tolist()[0] for pid in
                                         collaborative_recommendations_idx]
    # print("协同过滤推荐结果：")
    #print(collaborative_recommendations_idx)
    # 混合推荐
    combined_indices = list(set(content_recommendations_idx + collaborative_recommendations_idx))
    # print("混合推荐结果：")
    #print(combined_indices)
    return combined_indices
    # 获取具体细节
    # recommended_products = products.iloc[combined_indices].copy()
    # recommended_products = recommended_products[['good_int_id', 'product_id', 'product_name']]


def main(good_id=0):
    # 读取文件
    df = pd.read_csv("D:\\研究生\\课程\\数据挖掘\\大作业\\newbee-mall-spring-boot-3.x\\newbee-mall-spring-boot-3.x\\src\\main\\java\\ltd\\newbee\\mall\\util\\amazon(1).csv", encoding='utf-8')
    df = df.dropna()
    df = df.drop_duplicates()
    #print("列名：", df.columns.tolist())

    # 格式转换
    df['discounted_price'] = df['discounted_price'].astype(str).str.replace('₹', '').str.replace(',', '').astype(float)
    df['actual_price'] = df['actual_price'].astype(str).str.replace('₹', '').str.replace(',', '').astype(float)
    df['discount_percentage'] = df['discount_percentage'].astype(str).str.replace('%', '').astype(float)
    df['rating'] = pd.to_numeric(df['rating'].astype(str).str.replace('|', '', regex=True), errors='coerce')
    df['rating_count'] = df['rating_count'].astype(str).str.replace(',', '').astype(int)
    #print("格式转换")

    # 清理文本
    # print(df['product_name'])
    df['product_name'] = df['product_name'].apply(clean_text)
    df['about_product'] = df['about_product'].apply(clean_text)
    df['review_content'] = df['review_content'].apply(clean_text)
    # print(df['product_name'])
    # print("_____________")
    # print(df['category'])

    # 压缩类别
    df['category'] = df['category'].apply(lambda x: x.split('|')[0] if pd.notnull(x) else x)
    df['category'] = df['category'].apply(clean_text)
    # print(df['category'])

    # 情感分析
    reviews = df['review_content']
    reviews_sentiments = reviews.apply(sentiment_analysis)
    df['sentiment'] = reviews_sentiments
    # print(df['sentiment'])
    label_encoder = LabelEncoder()
    # 安装编码器并转换“情绪”栏
    df['encoded_sentiment'] = label_encoder.fit_transform(df['sentiment'])
    # print(df['encoded_sentiment'])

    # 删除无关列
    drop_col = ['discounted_price', 'actual_price', 'discount_percentage', 'review_id', 'review_title',
                       'user_name', 'img_link', 'product_link']
    df = df.drop(columns=drop_col)

    # 基于文本推荐，TF-IDF
    df['combined_text'] = df['product_name'] + ' ' + df['category'] + ' ' + df['about_product'] + ' ' + df['review_content']
    # 处理空字符情况
    df['combined_text'] = df['combined_text'].fillna('')
    # print("列名：", df.columns.tolist())
    # TF-IDF矢量器
    vectorizer = TfidfVectorizer(stop_words='english', max_df=0.95, min_df=2, ngram_range=(1, 1))
    tfidf_matrix = vectorizer.fit_transform(df['combined_text'])
    cosine_sim = cosine_similarity(tfidf_matrix)

    # 构建相似度矩阵，以平均值填补空缺
    product_user_matrix = df.pivot_table(index='product_id', values='rating', aggfunc='mean')
    product_user_matrix = product_user_matrix.fillna(product_user_matrix.mean())

    filtered_df = df[df['good_int_id'] == good_id]
    sample_product_id = filtered_df.iloc[0]['product_id']
    sample_product_name = filtered_df.iloc[0]['product_name']
    recommended_products = hybrid_recommendation(sample_product_id, cosine_sim, product_user_matrix, df)
    # print("Recommendation for user who purchased product \"" + sample_product_name + "\"")
    print(recommended_products)
    # return recommended_products


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(int(sys.argv[1]))
    else:
        print("Please provide a good_id as an argument.")


