# Django eCommerce Application Part 2 — REST API Plan

## Purpose

This API allows third-party clients to retrieve information from the eCommerce website. Authenticated vendors can create stores and add products. Authenticated buyers can submit product reviews.

## Representation Format

The API uses JSON because it is readable, easy to test and directly supported by Django REST Framework.

## Models

### Store

Fields:

* `id`
* `vendor`
* `vendor_username`
* `name`
* `description`
* `created_at`

### Product

Fields:

* `id`
* `store`
* `store_name`
* `name`
* `description`
* `price`
* `stock_quantity`
* `created_at`

### Review

Fields:

* `id`
* `product`
* `product_name`
* `buyer`
* `buyer_username`
* `rating`
* `comment`
* `created_at`

## API Endpoints

| Method | Endpoint                              | Purpose                         | Access               |
| ------ | ------------------------------------- | ------------------------------- | -------------------- |
| GET    | `/api/stores/`                        | View all stores                 | Public               |
| POST   | `/api/stores/`                        | Create a new store              | Authenticated vendor |
| GET    | `/api/vendors/<vendor_id>/stores/`    | View stores owned by one vendor | Public               |
| GET    | `/api/stores/<store_id>/products/`    | View store products             | Public               |
| POST   | `/api/stores/<store_id>/products/`    | Add product to owned store      | Store owner          |
| GET    | `/api/products/<product_id>/reviews/` | View product reviews            | Public               |
| POST   | `/api/products/<product_id>/reviews/` | Add product review              | Authenticated buyer  |
| GET    | `/reddit/`                            | View Reddit posts               | Public               |

## Authentication and Authorisation

The API uses Basic Authentication and Django Session Authentication.

A user creating a store becomes the vendor owner of that store. A product can only be added by the authenticated owner of that store. Reviews are linked to the authenticated buyer.

## Third-Party API Integration

The application fetches posts from Reddit's public JSON endpoint for the `django` subreddit. The Reddit page displays each post title, author and clickable original post link.
