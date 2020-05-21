import scrapy
import re
class FifaScrapper(scrapy.Spider):
    name='fifa'
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
            yield scrapy.Request(url=url,callback=self.get_all_players)
    def get_all_players(self,response):
        for row in response.css('tr'):
            lien = row.css('figure.player a::attr(href)').get()
            if lien:
                if '/player/' in lien:
                    eq = row.css('a.link-team')
                    if eq:
                        nom_eq = row.css('img.team').xpath('@alt').extract()[0]
                        rq = response.follow(lien,callback=self.get_players,meta={'teamT':nom_eq})
                        yield rq 
        if len(response.xpath('/html/body/main/div/div[2]/div[2]/nav[2]/ul/li/a/@href')) >1:
            lien = 'https://fifaindex.com'+response.xpath('/html/body/main/div/div[2]/div[2]/nav[2]/ul/li/a/@href')[1].extract()
            yield response.follow(lien,callback=self.get_all_players)
        elif re.search('fifa..',response.request.url.split('/')[-2]):
            lien = 'https://fifaindex.com'+response.xpath('/html/body/main/div/div[2]/div[2]/nav[2]/ul/li/a/@href')[0].extract()
            yield response.follow(lien,callback=self.get_all_players)
    def get_players(self,response):
        for i in response.xpath('/html/body/main/div/div[2]/div[2]/nav/ol/li[3]/div/a'):
            rq = response.follow('https://www.fifaindex.com'+i.xpath('@href').get(),callback=self.get_player_info,meta={'teamT':response.meta['teamT']})
            yield rq
    def get_player_info(self,response):
        try:
            nom = response.css('div.row.pt-3').css('div.col-sm-6')[1].css('h5.card-header::text').extract_first()
        except:
            nom=''
        try:
            overall=response.css('div.row.pt-3').css('div.col-sm-6')[1].css('h5.card-header').css('span.float-right').css('span::text').extract_first()
        except:
            overall=''
        try:
            potential = response.css('div.row.pt-3').css('div.col-sm-6')[1].css('h5.card-header').css('span.float-right').css('span::text')[2].extract()
        except:
            potential=''
        try:
            ddn=response.css('div.row.pt-3').css('div.col-sm-6')[1].css('div.card-body').css('p').css('span.float-right::text')[1].extract()
        except:
            ddn=''
        try:
            age=response.css('div.row.pt-3').css('div.col-sm-6')[2].css('div.card-body').css('p').css('span.float-right::text')[1].extract()
        except:
            age=''
        try:
            valeur =response.css('div.row.pt-3').css('div.col-sm-6')[4].css('div.card-body').css('p').css('span.float-right::text')[1].extract()
        except:
            valeur = ''
        try:
            salaire = response.css('div.row.pt-3').css('div.col-sm-6')[7].css('div.card-body').css('p').css('span.float-right::text')[1].extract()
        except:
            salaire= ''
        try:
            postes=  response.xpath('/html/body/main/div/div[2]/div[2]/div[2]/div[2]/div/div/p[6]/span/a/span/text()').extract()
        except:
            postes=''
        try:
            taille = response.xpath('/html/body/main/div/div[2]/div[2]/div[2]/div[2]/div/div/p[1]/span/span[1]/text()').extract()[0]
        except:
            taille=''
        try:
            plongeon= response.xpath('/html/body/main/div/div[2]/div[2]/div[4]/div[7]/div/div/p[2]/span/span/text()').extract()
        except:
            plongeon=''
        try:
            reflexe= response.xpath('/html/body/main/div/div[2]/div[2]/div[4]/div[7]/div/div/p[5]/span/span/text()').extract()
        except:
            reflexe=''
        try:
            marquage = response.xpath('/html/body/main/div/div[2]/div[2]/div[4]/div[2]/div/div/p[1]/span/span/text()').extract()
        except:
            marquage=''
        try:
            interception = response.xpath('/html/body/main/div/div[2]/div[2]/div[4]/div[3]/div/div/p[4]/span/span/text()').extract()
        except:
            interception=''
        try:
            finition = response.xpath('/html/body/main/div/div[2]/div[2]/div[4]/div[6]/div/div/p[3]/span/span/text()').extract()
        except:
            finition=''
        try:
            vitesse = response.xpath('/html/body/main/div/div[2]/div[2]/div[4]/div[5]/div/div/p[5]/span/span/text()').extract()
        except:
            vitesse=''
        try:
            passe_courtes = response.xpath('/html/body/main/div/div[2]/div[2]/div[4]/div[4]/div/div/p[2]/span/span/text()').extract()
        except:
            passe_courtes =''
        try:
            nationalite = response.xpath('/html/body/main/div/div[2]/div[2]/div[2]/div[1]/div[1]/div[2]/h2/a[2]/text()').extract()
        except:
            nationalite =''
        try:
            team = response.xpath('/html/body/main/div/div[2]/div[2]/div[3]/div[1]/div/h5/a[2]/text()').extract()
        except:
            team = ''
        numero = response.xpath('/html/body/main/div/div[2]/div[2]/div[3]/div[2]/div/div/p[2]/span/text()').extract()
        yield {
            'name': nom,
            'date':response.xpath('/html/body/main/div/div[2]/div[2]/nav/ol/li[3]/a/text()').extract(),
            'namev': nom +'_'+response.request.url.split('/')[-2],
            'numero':numero,
            'raw team': response.meta['teamT'],
            'position': postes,
            'overall':overall,
            'potentiel':potential,
            'DateNaissance':ddn,
            'age':age,
            'taille':taille,
            'valeur':valeur,
            'salaire':salaire,
            'plongeon':plongeon,
            'finition':finition,
            'vitesse':vitesse,
            'interception':interception,
            'marquage':marquage,
            'reflexe':reflexe,
            'passe courtes':passe_courtes,
            'nationalite': nationalite[0],
            'url': response.request.url
        }

