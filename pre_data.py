import json
import nltk
import nltk.data
from nltk.tokenize import RegexpTokenizer
#from compiler.ast import flatten
import sys,os
import numpy as np
from gensim import corpora, models, similarities


def splitSentence(paragraph):
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    sentences = tokenizer.tokenize(paragraph)
    return sentences

from nltk.tokenize import WordPunctTokenizer
def wordtokenizer(sentence):
#    toker = RegexpTokenizer(r'((?<=[^\w\s])\w(?=[^\w\s])|(\W))+', gaps=True)
    words = WordPunctTokenizer().tokenize(sentence)
#    words=toker.tokenize(sentence)
    return words

def word2vector(path,stoplist):
    file=open(path)
    contents=[]
    titles=[]
    for line in file.readlines():
        line =json.loads(line)
        id=line['id']
        print(id)
        content=line['content'].replace('\"','"')
        content=content.replace(u'\u2014','-').replace(u'\u201c','"').replace(u'\u201d','"').replace(u'\u2013','-').replace(u'\u2018',"'").replace(u'\u2019',"'")
        title=line['title']
        title=wordtokenizer(title)
        titles.append(title)
        sentences=splitSentence(content)
        sentences_list=[]
        for sentence in sentences:
            words=wordtokenizer(sentence)
            words=[word.lower() for word in words if word not in stoplist]
            sentences_list=sentences_list+words
        contents.append(sentences_list)
        title_content=sentences_list+title
    file.close()
    return contents,titles,title_content

path_base='../data/'
path=path_base+'corpus.txt'
stoplist=set('\ , .  ( ) - ? / ! : ; !.'.split())
contents,titles,title_content=word2vector(path,stoplist)
from gensim.models import Word2Vec
model1 = Word2Vec(title_content, size=128, window=5, min_count=1, workers=100)
model2 =Word2Vec(contents, size=128, window=5, min_count=1, workers=100)
model1.save(path_base+'bytecup.1.models')
model2.save(path_base+'bytecup.2.models')

#suma=sum(model.wv.vectors)
#t=['21','stories','our','readers','love','in','2017']
#val=[]
#for ts in t:
#    val.append(model.wv[ts])
#sumb=sum(np.array(val))
#print(suma,sumb)

def cos_len(a,b):
    lena=np.sqrt(a.dot(a))
    lenb=np.sqrt(b.dot(b))
    coslen=a.dot(b)/(lena*lenb)
    angel=np.arccos(coslen)
    angel=angel*360/2/np.pi
    return angel
#print(model.similarity('love','loved'))
#for title in titles[0]:
#    print(model.wv[title.lower()])
#   print(model.similarity())

dictionary = corpora.Dictionary(contents)
#print(dictionary.token2id)
dictionary.save(path_base+'bytecup.dict')  # store the dictionary, for future reference
corpus_con = [dictionary.doc2bow(content) for content in contents]
corpus_title=[dictionary.doc2bow(title) for title in titles]
corpora.MmCorpus.serialize(path_base+'bytecup_content.mm', corpus_con)  # store to disk, for later use
corpora.MmCorpus.serialize(path_base+'bytecup_title.mm', corpus_title)
corpus_con = corpora.MmCorpus(path_base+'bytecup_content.mm')
corpus_title = corpora.MmCorpus(path_base+'bytecup_title.mm')

tfidf = models.TfidfModel(corpus_con)
corpus_tfidf_con = tfidf[corpus_con]
corpus_tfidf_title = tfidf[corpus_title]
corpora.MmCorpus.serialize(path_base+'bytecup_tfidf_con.mm', corpus_tfidf_con)
corpora.MmCorpus.serialize(path_base+'bytecup_tfidf_title.mm', corpus_tfidf_title)

file=open(path_base+'train.data','w')
file.write(str(contents))
file.close()
file=open(path_base+'label.data','w')
file.write(str(titles))
file.close()
file=open(path_base+'title_content.data','w')
file.write(str(title_content))
file.close()
