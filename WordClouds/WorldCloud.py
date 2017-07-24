wd={}
# lines = open( "./count/BMW.csv", "r" )
with open("./count/BMW.csv", "r", encoding='utf8') as frN:
 lines = frN.read().split('\n')
for line in lines:
 if wd.get(line.replace('\n', '')) is None:#.decode('utf-8')
  wd[line.replace('\n', '')] = 1
 else:
  wd[line.replace('\n', '')]=wd.get(line.replace('\n', '').decode('utf-8'))+1
from pytagcloud import create_tag_image, make_tags
from pytagcloud.lang.counter import get_tag_counts
from operator import itemgetter
swd = sorted(wd.items(), key=itemgetter(1), reverse=True)
swd = swd[1:50]
tags = make_tags(swd, minsize=1,maxsize=50)
print(tags)
create_tag_image(tags, './wordcloud.png', background=(0, 0, 0, 255), size=(600, 400), fontname='msjhbd')

from wordcloud import WordCloud
cloud = WordCloud(background_color="white")
cloud.generate_from_frequencies(dict(data))
import matplotlib.pyplot as plt
plt.figure(figsize=(20,10))
plt.imshow(cloud, interpolation='bilinear')
plt.axis("off")
plt.show()
