# MyShelf: A Personal Collection Manager

#### Video Demo:

---

## Description

**MyShelf** is a Flask-based web application that allows users to manage their personal collections of books, figures, and Funko Pops from a single, unified interface. Think of it as a customizable digital shelf—one where each item is visually represented, categorized, and enhanced with metadata.

Books can be searched and added via the **Google Books API**, while figures and Funkos are sourced from **pre-loaded CSV files**. Each item added appears in a responsive grid layout that supports filtering, sorting, quantity tracking, and easy navigation. MyShelf aims to offer both functionality and beauty in a simple and intuitive experience.

---

## File Overview

* `app.py`
  The core Flask application containing all route definitions, session management, API calls, sorting/filtering logic, and database interactions.

* `templates/`
  Jinja2 HTML templates rendered by Flask:

  * `layout.html`: Base template with a sticky navigation bar.
  * `index.html`: Homepage with category selection.
  * `login.html` / `register.html`: Authentication pages.
  * `profile.html`: Displays the user’s entire collection with sorting and filtering options.
  * `books.html`, `funkos.html`, `figures.html`: Category-specific pages for browsing and adding items.

* `static/`
  Custom CSS for styling the layout and UI consistency across devices. Also includes icons and assets used throughout the app.

* `funkos.csv` / `figures.csv`
  Contain preloaded metadata for Funko Pops and figures respectively, since there is no free public API for them.

* `myshelf.db`
  SQLite database that stores user information, item metadata, and user collections.

* `helpers.py`
  Contains the `login_required` decorator to enforce authentication for protected routes.

* `requirements.txt`
  Specifies all required Python packages:

  * Flask
  * Flask-Session
  * requests
  * Werkzeug
  * and others

---

## Key Features

* User Authentication

  * Secure registration and login system
  * Passwords hashed using Werkzeug
  * Sessions managed via Flask-Session

* Google Books Integration

  * Users can search books via Google Books API
  * Paginated results with thumbnail, author, and title
  * Items can be added without redirecting or losing place

* CSV-Based Item Loading

  * Funkos and figures loaded from `csv` files

* User Profile View

  * Displays a user’s entire collection
  * Quantity tracked via `COUNT()` queries
  * Sorting options: Newest, Oldest, A-Z, Z-A, Category, Series

* Dynamic and Sticky Navbar

  * Category links appear dynamically and contextually
  * Navigation bar stays visible while scrolling
  * Category links left-aligned, auth/profile links right-aligned

* Responsive and Modern UI

  * Built with Bootstrap 5
  * Uniform card design with consistent spacing and hover effects

---

## Design Decisions

* API vs CSV Loading:
  Books are fetched live from the Google Books API and stored via `google_id`. This keeps the DB clean and avoids redundancy. Funkos and figures are locally stored in CSV due to the absence of reliable public APIs.

* Quantity via Row Counting:
  Instead of storing quantity as a field, each addition is a new row. This simplifies logic and prevents synchronization issues when modifying collections.

* Redirect Preservation for UX:
  To prevent page reloads disrupting user flow, especially when browsing through pages of books, item additions redirect back to the current page using `url_for(from_page)`.

* Simplified Schema:
  Books are not added to a central `items` table. They’re tracked directly in the `collections` table using their unique `google_id`, avoiding unnecessary joins and storage.

* User-Friendly Design:
  Focused on intuitive layout, responsive design, and minimal clicks for common actions.

---

## Future Improvements

* Implement **infinite scrolling** for book search using AJAX.
* Display **collection statistics** (e.g., total items, favorite category).
* Add **notes or tags** to individual items.
* Support **collection sharing** via public URLs or exporting to CSV.
* Add **user-created entries** for a more personalized experience, as the figures and funkos categories are quite limited, it would be ideal for users to be able to input their own items when needed.

---

## Credits

* **ChatGPT (OpenAI)**: Helped in code debugging, UI feedback, and documentation.
* **Google Books API**: For real-time book metadata and images.
* **Bootstrap 5**: Frontend framework for responsive design.
* **CS50 Library**: Ideas and structural guidance.
* **Flask** and **Werkzeug**: Web framework and security.

---

## Final Thoughts

**MyShelf** was built for collectors who want a centralized, beautiful, and functional place to manage their physical media and merchandise collections. It simplifies adding, browsing, and managing a growing personal inventory while maintaining a pleasant user experience.

This is not just a CRUD app—MyShelf is designed to evolve, with thoughtful touches like session-aware redirects, real-time API integration, and a design that scales with its user’s collection. It lays a solid foundation for future feature growth and real-world deployment.
