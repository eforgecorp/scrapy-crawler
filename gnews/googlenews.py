from gnews import GNews
import json
google_news = GNews()


def get_articles(topic:str):
    test_news = google_news.get_news_by_topic(topic.upper())
    news = []
    for item in test_news:
        full_article = google_news.get_full_article(item['url'])
        
        # Checking if any link throw error, to prevent crush of the application
        try:
            singleNews = {
                "title": f"{item['title']}",
                "brief": f"{item['description']}",
                "body": f"{full_article.text}",
                "publisher": f"{item['publisher']}",
            }
            # adding every single in news array as a dictionary
            news.append(singleNews)
        except:
            continue
        
    # finally save all the news as json file
    with open(f'{topic}.json', 'w') as json_file:
        json.dump(news, json_file)

# Getting Input  
topic = input("Write a topic: ")
get_articles(topic)
