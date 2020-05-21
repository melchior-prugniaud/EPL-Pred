import scrapy
import re
class FifaTeamScrapper(scrapy.Spider):
    name='fifa_team'
    def start_requests(self):
        urls=["https://www.fifaindex.com/players/fifa20/",
            "https://www.fifaindex.com/players/fifa19/",
            "https://www.fifaindex.com/players/fifa18/",
            "https://www.fifaindex.com/players/fifa17/",
            "https://www.fifaindex.com/players/fifa16/",
            "https://www.fifaindex.com/players/fifa15/",
            "https://www.fifaindex.com/players/fifa14/",
            "https://www.fifaindex.com/players/fifa13/",
            "https://www.fifaindex.com/players/fifa12/",
            "https://www.fifaindex.com/players/fifa11/",
            "https://www.fifaindex.com/players/fifa10/"
        ]
        for url in urls:
            yield scrapy.Request(url=url,callback=self.get_all_teams)
    def get_all_teams(self,response):
        liens = [lien.extract() for lien in response.css('td a::attr(href)')]
        for lien in liens:
            if '/team/' in lien:
                rq = response.follow(lien,callback=self.get_team)
                yield rq 
        if len(response.xpath('/html/body/main/div/div[2]/div[2]/nav[2]/ul/li/a/@href')) >1:
            lien = 'https://fifaindex.com'+response.xpath('/html/body/main/div/div[2]/div[2]/nav[2]/ul/li/a/@href')[1].extract()
            yield response.follow(lien,callback=self.get_all_teams)
        else:
            lien = 'https://fifaindex.com'+response.xpath('/html/body/main/div/div[2]/div[2]/nav[2]/ul/li/a/@href')[0].extract()
            yield response.follow(lien,callback=self.get_all_teams)
    def get_team(self,response):
        for i in response.xpath('/html/body/main/div/div[2]/div[2]/nav/ol/li[3]/div/a'):
            rq = response.follow('https://www.fifaindex.com'+i.xpath('@href').get(),callback=self.get_team_info)
            yield rq
    def get_team_info(self,response):
        attaque = response.xpath('/html/body/main/div/div[2]/div[2]/div[2]/div[2]/div/ul/li[2]/span/span/text()').extract()
        milieu=response.xpath('/html/body/main/div/div[2]/div[2]/div[2]/div[2]/div/ul/li[3]/span/span/text()').extract()
        defense=response.xpath('/html/body/main/div/div[2]/div[2]/div[2]/div[2]/div/ul/li[4]/span/span/text()').extract()
        equipe = response.xpath('/html/body/main/div/div[2]/div[2]/div[2]/div[1]/div[1]/div[2]/h1/text()').extract()
        date = response.xpath('/html/body/main/div/div[2]/div[2]/nav/ol/li[3]/a/text()').extract()[0]
        champ =response.xpath('/html/body/main/div/div[2]/div[2]/div[2]/div[1]/div[1]/div[2]/h2/a/text()').extract()[0]
        yield{
            'Equipe':equipe[0],
            'Attaque':attaque[0],
            'Milieu':milieu[0],
            'Défense':defense[0],
            'Championnat':champ,
            'Date':date
        }