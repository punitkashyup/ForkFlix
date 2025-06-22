# 🚀 Recipe Reel Manager

A modern, full-stack web application for saving and organizing Instagram food recipes with AI-powered extraction capabilities.

## ✨ Features

### 🎯 Core Features
- **Instagram Integration**: Save recipes directly from Instagram reels and posts
- **AI-Powered Extraction**: Automatic ingredient and recipe information extraction using Hugging Face models
- **Smart Categorization**: Auto-categorize recipes (Starters, Main Course, Desserts, etc.)
- **Recipe Management**: Full CRUD operations for recipe management
- **User Authentication**: Secure Firebase authentication
- **Responsive Design**: Mobile-first, fully responsive interface
- **Progressive Web App**: Offline functionality with service worker
- **Real-time Animations**: Smooth Framer Motion animations and Lottie graphics

### 🤖 AI Capabilities
- **Image Analysis**: Extract ingredients from video thumbnails
- **Text Processing**: Parse captions for recipe information
- **Cooking Time Prediction**: Estimate preparation time
- **Dietary Detection**: Identify dietary restrictions (vegan, gluten-free, etc.)
- **Smart Tagging**: Auto-generate relevant tags

### 📱 Mobile Features
- **Touch-Friendly Interface**: 44px minimum touch targets
- **Swipe Gestures**: Recipe card interactions
- **Pull-to-Refresh**: Refresh recipe lists
- **Offline Viewing**: Access saved recipes without internet
- **Web Share API**: Native sharing capabilities

## 🛠 Tech Stack

### Frontend
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **Lottie React** for micro-animations
- **React Hook Form** for form management
- **React Router v6** for navigation
- **Firebase SDK** for authentication
- **Axios** for API communication

### Backend
- **FastAPI** with Python 3.11+
- **Firebase Admin SDK** for database and auth
- **Hugging Face Transformers** for AI processing
- **Pydantic** for data validation
- **Uvicorn** ASGI server
- **HTTPx** for async HTTP requests

### Services
- **Firebase Firestore** for database
- **Firebase Storage** for media files
- **Firebase Authentication** for user management
- **Hugging Face API** for AI models
- **Instagram oEmbed API** for content embedding

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ and npm
- Python 3.11+
- Firebase project
- Hugging Face API key
- Facebook App (for Instagram API access)

### Installation

#### Option 1: Automated Setup (Recommended)

```bash
git clone <repository-url>
cd ForkFlix
python scripts/setup.py
```

This script will automatically:
- Install all dependencies
- Create environment files
- Guide you through Firebase and Instagram API setup
- Test your configuration

#### Option 2: Manual Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ForkFlix
   ```

2. **Setup Backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Setup Frontend**
   ```bash
   cd frontend
   npm install
   ```

4. **Environment Configuration**
   
   Backend `.env`:
   ```bash
   FIREBASE_PROJECT_ID=forkflix-9e6b2
   FIREBASE_CREDENTIALS_PATH=../firebase/firebase-admin-key.json
   HUGGINGFACE_API_KEY=your_huggingface_api_key
   FACEBOOK_APP_ID=your_facebook_app_id
   FACEBOOK_APP_SECRET=your_facebook_app_secret
   SECRET_KEY=your_secret_key_here
   CORS_ORIGINS=http://localhost:3000
   ```

   Frontend `.env`:
   ```bash
   REACT_APP_API_URL=http://localhost:8000
   REACT_APP_FIREBASE_API_KEY=your_firebase_api_key
   REACT_APP_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
   REACT_APP_FIREBASE_PROJECT_ID=forkflix-9e6b2
   REACT_APP_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
   REACT_APP_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
   REACT_APP_FIREBASE_APP_ID=your_app_id
   ```

5. **Firebase Setup**
   - Place your Firebase admin key in `firebase/firebase-admin-key.json`
   - Deploy Firestore rules: `firebase deploy --only firestore:rules,firestore:indexes --project <alias_or_project_id>`

6. **Instagram API Setup**
   
   **Option 1: Automated Setup (Recommended)**
   ```bash
   python scripts/setup_instagram_token.py
   ```
   
   **Option 2: Manual Setup**
   - Create a Facebook App at [developers.facebook.com](https://developers.facebook.com/)
   - Get your App ID and App Secret
   - Add them to your backend `.env` file
   
   **📚 Detailed Guide**: See [Instagram Access Token Guide](docs/INSTAGRAM_ACCESS_TOKEN_GUIDE.md)

7. **Start Development Servers**
   ```bash
   # Terminal 1 - Backend
   cd backend
   uvicorn app.main:app --reload

   # Terminal 2 - Frontend
   cd frontend
   npm start
   ```

## 📁 Project Structure

```
ForkFlix/
├── 📁 frontend/                  # React TypeScript Frontend
│   ├── 📁 public/               # Static assets and PWA files
│   ├── 📁 src/
│   │   ├── 📁 components/       # React components
│   │   │   ├── 📁 common/       # Reusable UI components
│   │   │   ├── 📁 recipe/       # Recipe-specific components
│   │   │   └── 📁 layout/       # Layout components
│   │   ├── 📁 pages/            # Page components
│   │   ├── 📁 context/          # React Context for state
│   │   ├── 📁 services/         # API services
│   │   ├── 📁 hooks/            # Custom React hooks
│   │   ├── 📁 types/            # TypeScript type definitions
│   │   └── 📁 config/           # Configuration files
│   └── package.json
├── 📁 backend/                  # FastAPI Python Backend
│   ├── 📁 app/
│   │   ├── 📁 api/              # API endpoints
│   │   ├── 📁 models/           # Pydantic models
│   │   ├── 📁 services/         # Business logic services
│   │   ├── 📁 core/             # Core configuration
│   │   └── 📁 schemas/          # API schemas
│   └── requirements.txt
├── 📁 firebase/                 # Firebase configuration
├── 📁 docs/                     # Documentation
└── 📁 scripts/                  # Utility scripts
```

## 🔧 Development

### Available Scripts

**Frontend:**
```bash
npm start          # Start development server
npm run build      # Build for production
npm test          # Run tests
```

**Backend:**
```bash
uvicorn app.main:app --reload    # Start development server
pytest                           # Run tests
black .                         # Format code
```

**Root:**
```bash
npm run setup     # Initial project setup
npm run dev       # Start both frontend and backend
npm run build     # Build frontend for production
```

## 📝 API Documentation

The API documentation is available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Key Endpoints

- `POST /api/v1/recipes/` - Create recipe from Instagram URL
- `GET /api/v1/recipes/` - List recipes with pagination
- `GET /api/v1/recipes/{id}` - Get single recipe
- `PUT /api/v1/recipes/{id}` - Update recipe
- `DELETE /api/v1/recipes/{id}` - Delete recipe
- `POST /api/v1/instagram/validate` - Validate Instagram URL
- `POST /api/v1/ai/extract-ingredients` - AI ingredient extraction

## 🎨 Design System

### Color Palette
- **Primary**: Blue gradient (#0ea5e9 → #3b82f6)
- **Secondary**: Purple gradient (#d946ef → #c026d3)
- **Success**: #10b981
- **Error**: #ef4444
- **Warning**: #f59e0b

### Typography
- **Display**: Poppins
- **Body**: Inter
- **Code**: Source Code Pro

## 🧪 Testing

### Frontend Testing
```bash
cd frontend
npm test
```

### Backend Testing
```bash
cd backend
pytest
```

## 🚀 Deployment

### Frontend (Vercel)
1. Connect your GitHub repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main branch

### Backend (Railway/Render)
1. Connect your GitHub repository
2. Set environment variables
3. Deploy with auto-scaling enabled

### Firebase
```bash
cd firebase
firebase deploy
```

## 🔐 Security

- Firebase Authentication for user management
- Firestore security rules for data protection
- Input validation and sanitization
- Rate limiting on AI endpoints
- CORS configuration for cross-origin requests

## ⚡ Performance

- **Frontend**: Code splitting, lazy loading, image optimization
- **Backend**: Async operations, connection pooling, caching
- **Database**: Indexed queries, pagination
- **AI**: Model caching, request batching

## 🌐 Browser Support

- Chrome/Edge 88+
- Firefox 85+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## 📱 PWA Features

- **Offline Support**: Cache recipes for offline viewing
- **Add to Home Screen**: Install as native app
- **Push Notifications**: Recipe reminders (planned)
- **Background Sync**: Upload recipes when back online

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- 📧 Email: support@recipemanager.com
- 🐛 Issues: [GitHub Issues](https://github.com/username/recipe-manager/issues)
- 📚 Docs: [Documentation](./docs/)

## 🙏 Acknowledgments

- [Hugging Face](https://huggingface.co/) for AI models
- [Firebase](https://firebase.google.com/) for backend services
- [Instagram](https://www.instagram.com/) for oEmbed API
- [Tailwind CSS](https://tailwindcss.com/) for styling
- [Framer Motion](https://www.framer.com/motion/) for animations

---

**Built with ❤️ by the Recipe Reel Manager Team**