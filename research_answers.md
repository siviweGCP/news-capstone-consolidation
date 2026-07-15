# Practical Task 2 Research Answers

## 1. Python Requests Module

The Python `requests` module is a third-party library used to send HTTP requests from a Python program. It allows a developer to communicate with websites, APIs, and web services using common HTTP methods such as `GET`, `POST`, `PUT`, `PATCH`, and `DELETE`.

A `GET` request is normally used to retrieve information from a server. For example, an application can request a list of products from an API. A `POST` request is normally used to send new information to a server, such as submitting a registration form or creating a new product. `PUT` and `PATCH` are commonly used to update existing data, while `DELETE` is used to remove data.

The `requests` module makes HTTP communication easier because it hides many of the complicated details of working with HTTP manually. It can send data, handle headers, pass authentication details, work with JSON responses, and read status codes. This makes it useful when building applications that need to connect to external APIs or other web services.

Example:

```python
import requests

response = requests.get("https://api.example.com/products")

if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print("Request failed")
```

In this example, Python sends a request to an API. If the server responds successfully, the program converts the JSON response into Python data that can be used in the application.

---

## 2. JSON and XML Data Formats

## JSON

JSON stands for JavaScript Object Notation. It is a lightweight data format used to store and exchange data between systems. JSON is commonly used in web APIs because it is simple, readable, and easy for many programming languages to process.

A JSON example:

```json
{
    "name": "Laptop",
    "price": 8999.99,
    "in_stock": true
}
```

### Uses of JSON

JSON is used to transfer data between a client and a server, especially in RESTful APIs. It is also used in configuration files, mobile applications, web applications, and data storage where a simple structure is required.

### Advantages of JSON

1. JSON is easy for humans to read and write.
2. JSON is lightweight, meaning it does not use too many extra characters.
3. JSON works well with many programming languages, including Python and JavaScript.
4. JSON is easy to convert into objects, dictionaries, or arrays in programming languages.

### Disadvantages of JSON

1. JSON does not support comments, which can make documentation inside files difficult.
2. JSON is less suitable for very complex document structures.
3. JSON does not provide strong built-in validation rules by itself.
4. JSON only supports a limited number of data types compared to some other formats.

---

## XML

XML stands for Extensible Markup Language. It is a markup-based data format used to store and transport structured data. XML uses tags to describe data, which makes it flexible and descriptive.

An XML example:

```xml
<product>
    <name>Laptop</name>
    <price>8999.99</price>
    <in_stock>true</in_stock>
</product>
```

### Uses of XML

XML is used in systems that require structured documents, data exchange, configuration files, enterprise systems, and older web services. It is also used where strict document structure and validation are important.

### Advantages of XML

1. XML is flexible because developers can create their own tags.
2. XML can represent complex and nested data structures.
3. XML supports schemas, which help validate the structure of documents.
4. XML is widely supported in many older systems and enterprise applications.

### Disadvantages of XML

1. XML is more verbose than JSON because it uses opening and closing tags.
2. XML files are usually larger than JSON files containing the same data.
3. XML can be harder to read when the document becomes large.
4. XML parsing can be slower and more complicated than JSON parsing.

---

## 3. RESTful APIs

A RESTful API is an application programming interface that follows REST principles. REST stands for Representational State Transfer. It is a common way for software systems to communicate over the web using HTTP.

A RESTful API usually works with resources. A resource can be something like a user, product, order, store, or review. Each resource is accessed using a URL. For example:

```text
/products/
```

The API uses HTTP methods to decide what action should happen:

* `GET` retrieves data.
* `POST` creates new data.
* `PUT` replaces existing data.
* `PATCH` updates part of existing data.
* `DELETE` removes data.

For example, in an eCommerce application, a buyer may send a `GET` request to view products, while a vendor may send a `POST` request to add a new product.

### How RESTful APIs Work

A client, such as a web browser, mobile app, or frontend application, sends an HTTP request to the server. The server processes the request, interacts with the database if needed, and returns a response. The response is commonly returned in JSON format.

RESTful APIs are usually stateless. This means each request should contain the information needed for the server to understand and process it. The server does not need to remember previous requests in order to handle the current one.

### Uses of RESTful APIs

RESTful APIs are used to connect different software systems. They are commonly used in web applications, mobile apps, payment systems, eCommerce platforms, cloud services, and third-party integrations.

### Advantages of RESTful APIs

1. RESTful APIs are simple to understand because they use standard HTTP methods.
2. They can be used by different types of clients, including web, mobile, and desktop applications.
3. They are scalable because the client and server are separated.
4. They usually return JSON, which is lightweight and easy to process.

### Disadvantages of RESTful APIs

1. RESTful APIs can become difficult to manage when an application has many endpoints.
2. Too many requests may be needed to collect related data from different resources.
3. REST does not automatically enforce strict standards, so poor design can lead to inconsistent APIs.
4. Stateless communication means the client may need to send repeated authentication or context information with requests.

## Conclusion

The `requests` module, JSON, XML, and RESTful APIs are important tools and concepts in modern software development. The `requests` module allows Python applications to communicate with web services. JSON and XML are used to structure and exchange data. RESTful APIs allow different systems to communicate using standard HTTP methods. These concepts are especially useful in web applications such as eCommerce systems, where users, products, carts, invoices, and reviews may need to be exchanged between clients and servers.
