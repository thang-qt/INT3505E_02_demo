from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory database
books = [
    {"id": 1, "title": "Số đỏ", "author": "Vũ Trọng Phụng", "publisher": "NXB Văn học", "publication_year": 1936, "quantity": 5},
    {"id": 2, "title": "Dế Mèn phiêu lưu ký", "author": "Tô Hoài", "publisher": "NXB Kim Đồng", "publication_year": 1941, "quantity": 10},
    {"id": 3, "title": "Tắt đèn", "author": "Ngô Tất Tố", "publisher": "NXB Văn học", "publication_year": 1937, "quantity": 7},
    {"id": 4, "title": "Lão Hạc", "author": "Nam Cao", "publisher": "NXB Hội Nhà văn", "publication_year": 1943, "quantity": 3},
    {"id": 5, "title": "Truyện Kiều", "author": "Nguyễn Du", "publisher": "NXB Văn học", "publication_year": 1820, "quantity": 2},
]

loans = []
next_loan_id = 1

# Get all books
@app.route('/books', methods=['GET'])
def get_books():
    return jsonify(books)

# Get a specific book
@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = next((book for book in books if book["id"] == book_id), None)
    if book:
        return jsonify(book)
    return jsonify({"message": "Book not found"}), 404

# Create a new book
@app.route('/books', methods=['POST'])
def create_book():
    new_book = {
        "id": len(books) + 1,
        "title": request.json['title'],
        "author": request.json['author'],
        "publisher": request.json['publisher'],
        "publication_year": request.json['publication_year'],
        "quantity": request.json['quantity']
    }
    books.append(new_book)
    return jsonify(new_book), 201

# Update a book
@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = next((book for book in books if book["id"] == book_id), None)
    if book:
        book['title'] = request.json.get('title', book['title'])
        book['author'] = request.json.get('author', book['author'])
        book['publisher'] = request.json.get('publisher', book['publisher'])
        book['publication_year'] = request.json.get('publication_year', book['publication_year'])
        book['quantity'] = request.json.get('quantity', book['quantity'])
        return jsonify(book)
    return jsonify({"message": "Book not found"}), 404

# Delete a book
@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    global books
    books = [book for book in books if book["id"] != book_id]
    return jsonify({"message": "Book deleted"})

# Borrow a book
@app.route('/borrow', methods=['POST'])
def borrow_book():
    global next_loan_id
    book_id = request.json['book_id']
    user_id = request.json['user_id']

    book = next((book for book in books if book["id"] == book_id), None)

    if not book:
        return jsonify({"message": "Book not found"}), 404

    if book['quantity'] > 0:
        loan = {
            "id": next_loan_id,
            "user_id": user_id,
            "book_id": book_id
        }
        loans.append(loan)
        book['quantity'] -= 1
        next_loan_id += 1
        return jsonify(loan), 201
    else:
        return jsonify({"message": "Book is out of stock"}), 400

# Return a book
@app.route('/return', methods=['POST'])
def return_book():
    loan_id = request.json['loan_id']

    loan = next((loan for loan in loans if loan["id"] == loan_id), None)

    if not loan:
        return jsonify({"message": "Loan not found"}), 404

    book = next((book for book in books if book["id"] == loan['book_id']), None)

    if book:
        book['quantity'] += 1

    loans.remove(loan)

    return jsonify({"message": "Book returned successfully"})

# Get all loans
@app.route('/loans', methods=['GET'])
def get_loans():
    return jsonify(loans)

if __name__ == '__main__':
    app.run(debug=True)
