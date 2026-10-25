def pokemonScrape(content):
    pokemon = {}

    name = content.find("h1", class_="product_title").text
    sku = content.find("span", class_="sku").text
    in_stock = content.find("p", class_="stock").text
    price = content.find("p", class_="price").text.strip("£")
    pokemon["name"] = name
    pokemon["sku"] = sku
    pokemon["in_stock"] = in_stock
    pokemon["price"] = price
    return pokemon


def carScrape(content):
    car = {}

    car["name"] = content.find("h2", class_="title").text
    car["price"] = content.find("span", attrs={"data-price": True})["data-price"]
    car["rating"] = content.find("div", attrs={"data-rating": True})["data-rating"]
    car["make"] = content.find("td", class_="make").text
    car["model"] = content.find("td", class_="model").text
    car["year"] = int(content.find("td", class_="year").text)
    car["engine"] = content.find("td", class_="engine").text
    car["drivetrain"] = content.find("td", class_="drivetrain").text
    car["power"] = int(
        content.find("td", class_="power")
        .text.replace("HP", "")
        .replace(" ", "")
        .strip()
    )
    car["countryOfOrigin"] = content.find("td", class_="country").text
    car["mileage"] = int(
        content.find("td", class_="mileage")
        .text.replace("km", "")
        .replace(" ", "")
        .strip()
    )
    car["condition"] = content.find("td", class_="condition").text
    car["exteriorColor"] = content.find("td", class_="exterior-color").text
    car["interiorColor"] = content.find("td", class_="interior-color").text
    car["bodyStyle"] = content.find("td", class_="body-style").text
    return car


def bookScrape(content):
    table = content.find("table", {"class": "table-striped"})
    columns = table.find_all("td")

    knjiga = {}
    knjiga["title"] = content.find("h1").text
    knjiga["UPC"] = (columns[0]).text
    price_text = (columns[2]).text
    price_text = price_text.lstrip("£")
    knjiga["price"] = price_text
    knjiga["tax"] = (columns[4]).text[1:]
    knjiga["in_stock"] = (columns[5]).text
    return knjiga
