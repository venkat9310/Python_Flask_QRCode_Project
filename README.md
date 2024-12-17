# Python_Flask_QRCode_Project
# QR Code Generator and Reader

## Project Overview

This project is a **QR Code Generator and Reader** web application built using **Python** and **Flask**. It allows users to:

1. Generate QR codes based on user input.
2. Read and decode QR codes.
3. View QR code contents.
4. Register and Sign in to access personalized features.

## Features

- **QR Code Generation**: Input text or data to generate a QR code.
- **QR Code Reading**: Upload or scan a QR code to view its content.
- **User Authentication**: Register and sign in to access the app.
- **Clean UI**: User-friendly interface with responsive design.

## Project Structure

```
QR_Code/
├── application.py            # Main Flask application
├── templates/                # HTML templates for web pages
│   ├── index.html            # Home page
│   ├── generate.html         # QR code generation page
│   ├── read.html             # QR code reading page
│   ├── register.html         # User registration page
│   ├── signin.html           # User sign-in page
│   ├── home.html             # Authenticated user's home page
│   └── view_qr_contents.html # View decoded QR content
└── static/                   # Static files (CSS, JS)
    ├── styles.css            # Main stylesheet
    ├── generate_script.js    # Script for generating QR codes
    ├── read_script.js        # Script for reading QR codes
    ├── register_script.js    # Script for user registration
    ├── signin_script.js      # Script for user sign-in
    └── view_qr_contents_script.js # Script for viewing QR content
```

## Installation

### Prerequisites

Ensure you have the following installed on your system:

- Python 3.x
- Flask
- Required Python libraries (listed below)

### Steps

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd QR_Code
   ```

2. Install required dependencies:

   ```bash
   pip install flask qrcode pillow
   ```

3. Run the application:

   ```bash
   python application.py
   ```

4. Open the app in your browser:

   ```
   http://127.0.0.1:5000
   ```

## Dependencies

The project uses the following Python libraries:

- **Flask**: Web framework for building the app.
- **qrcode**: To generate QR codes.
- **Pillow**: Image processing library for QR code handling.

Install them using:

```bash
pip install flask qrcode pillow
```

## Usage

1. **Home Page**: Navigate to the home page and choose an option:

   - Generate QR Code
   - Read QR Code
   - Register / Sign In

2. **Generate QR Code**:

   - Enter text or data.
   - Click on "Generate" to create a QR code.
   - Download the generated QR code.

3. **Read QR Code**:

   - Upload a QR code image.
   - The app will display the decoded content.

4. **Register / Sign In**:

   - Register a new account or sign in to access personalized features.

## Screenshots

- **Home Page**
- **Generate QR Code Page**
- **Read QR Code Page**
- **Register / Sign In Pages**

*(Add screenshots here)*

## Future Enhancements

- Add a database to store user-generated QR codes.
- Implement real-time QR code scanning using a webcam.
- Enhance user authentication with secure password hashing.

## License

This project is licensed under the MIT License.

## Contact

For any queries or suggestions, feel free to contact:

- **Your Name**
- **Email**: nvenkat9310@gmail.com



