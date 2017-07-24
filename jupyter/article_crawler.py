def article_crawler(url):
    article_dict = {}
    article_dict['url'] = url
    res2 = requests.get(url)
    soup2 = BeautifulSoup(res2.text, 'lxml')

    # handling artical-metaline author title board
    value_tags = soup2.select('span.article-meta-value')
    values = [val.text for val in value_tags]
    article_dict = {k: v for k, v in zip(['author', 'board', 'title', 'time'], values)}

    # finding ip
    span2 = soup2.select('span.f2')
    for span in span2:
        match = re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', span.text.strip())
        if match:
            article_dict['ip'] = match.group()

    # finding push (type, content, tm)
    push_list = []
    push_dict = {}
    pushs = soup2.select('div.push')

    for push in pushs:
        push_dict = {}
        push_dict['type'] = push.select_one('.push-tag').text
        push_dict['content'] = push.select_one('.push-content').text.replace(':', '').strip()
        push_dict['tm'] = push.select_one('.push-ipdatetime').text.strip()
        push_list.append(push_dict)

    article_dict['push'] = push_list

    # finding content
    main_content = soup2.select_one('#main-content')

    for div in main_content.find_all('div'):
        div.decompose()
    for span in main_content.find_all('span'):
        span.decompose()

    article_dict['content'] = ''.join(main_content.text.split())

    return article_dict