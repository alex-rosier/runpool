# Run Pool - Baseball Pool Management Application

A Flask-based web application for managing baseball "run pools" - a type of betting/gaming system where participants predict baseball game outcomes.

## 🏟️ Project Overview

Run Pool is a fantasy sports platform specifically designed for baseball run pools where:
- Users create games and invite players
- Players pick MLB teams
- The system tracks real MLB games and scores
- Players compete based on their team's performance
- Winners are determined by team run totals

## ✨ Features

### Core Functionality
- **User Management**: Registration, login, password reset with secure authentication
- **Game Creation**: Create new pool games with start dates and multiple players
- **Player Management**: Add both registered and non-registered players to games
- **Team Selection**: 30 MLB teams with proper abbreviations
- **Score Tracking**: Real-time MLB score updates via API
- **Scorecard Views**: Comprehensive game scorecards and standings
- **Game Management**: View active games, player standings, and delete games

### Technical Features
- **Real-time Updates**: Automated score calculation and updates
- **Secure Authentication**: Flask-Login with bcrypt password hashing
- **Database Management**: SQLAlchemy ORM with PostgreSQL/SQLite support
- **Email Integration**: Flask-Mail for notifications and password resets
- **Responsive UI**: Modern Bootstrap-based interface with custom CSS

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Apr-27-RUN-POOL
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   SECRET_KEY=your-secret-key-here
   DATABASE_URI=sqlite:///run_pool.db
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-email-password
   ```

5. **Initialize the database**
   ```bash
   python -c "from app_2025_latest import app, db; app.app_context().push(); db.create_all()"
   ```

6. **Run the application**
   ```bash
   python app_2025_latest.py
   ```

7. **Open your browser**
   Navigate to `http://127.0.0.1:5000`

## 🏗️ Project Structure

```
Apr-27-RUN-POOL/
├── app_2025_latest.py          # Main Flask application
├── alembic/                    # Database migration files
├── static/                     # CSS, JavaScript, and static assets
│   └── styles.css             # Custom styling
├── templates/                  # HTML templates
│   ├── base.html              # Base template
│   ├── create_game_new.html   # Game creation form
│   └── ...                    # Other templates
├── requirements.txt            # Python dependencies
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## 🗄️ Database Models

### Core Models
- **User**: Registered users with authentication
- **Team**: MLB teams (30 teams with proper abbreviations)
- **Game**: Individual pool games with tokens for sharing
- **Player**: Users participating in specific games
- **GameScore**: Real-time scores from MLB games
- **RunTotal**: Cumulative run totals for teams
- **NonRegisteredPlayer**: Players without user accounts

### Key Relationships
- Games have multiple Players
- Players can be registered Users or NonRegisteredPlayers
- Teams are associated with Players and GameScores
- Games track GameScores for real-time updates

## 🎮 How to Use

### Creating a Game
1. **Login** to your account
2. **Navigate** to "Create Game"
3. **Select** your team from the dropdown
4. **Add players** by entering names and selecting teams
5. **Set start date** for the pool
6. **Submit** to create the game

### Managing Players
- **Add players** to existing games
- **Remove players** from games
- **View standings** and scores
- **Share games** via unique tokens

### Viewing Results
- **Scorecards** show real-time standings
- **Team performance** tracked across games
- **Run totals** calculated automatically
- **Historical data** available for analysis

## 🔧 Configuration

### Environment Variables
- `SECRET_KEY`: Flask secret key for sessions
- `DATABASE_URI`: Database connection string
- `MAIL_USERNAME`: Email username for notifications
- `MAIL_PASSWORD`: Email password for notifications

### Database Options
- **SQLite** (default): `sqlite:///run_pool.db`
- **PostgreSQL**: `postgresql://user:password@localhost/dbname`

## 🧪 Testing

The application includes several test endpoints for development:
- `/test_gamescore` - Test GameScore creation
- `/test_update_player_scores` - Test score updates
- `/test_gamescores/<game_id>/<date>` - Test date-based queries

## 🚨 Known Issues & Fixes

### Recent Fixes Applied
- ✅ **Duplicate Game Creation**: Fixed logic that was creating multiple games
- ✅ **Player Management**: Proper handling of registered vs non-registered players
- ✅ **Form Validation**: Improved form structure and validation
- ✅ **Database Constraints**: Fixed unique constraint violations

### Common Issues
- **Database Lock**: Ensure only one instance is running
- **Email Configuration**: Verify SMTP settings in `.env`
- **Team Selection**: Ensure all 30 MLB teams are properly loaded

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

## 📝 Development Notes

### Code Style
- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add comments for complex logic
- Maintain consistent indentation

### Database Migrations
- Use Alembic for schema changes
- Test migrations on development data first
- Document breaking changes

### Security Considerations
- Never commit sensitive data (API keys, passwords)
- Use environment variables for configuration
- Validate all user inputs
- Implement proper authentication and authorization

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues:
1. Check the **Known Issues** section above
2. Review the **Configuration** section
3. Check the application logs for error messages
4. Open an issue on GitHub with detailed information

## 🔮 Future Enhancements

- [ ] Mobile app development
- [ ] Advanced statistics and analytics
- [ ] Social features and leaderboards
- [ ] Integration with more sports APIs
- [ ] Real-time notifications
- [ ] Advanced game types and scoring systems

---

**Happy Pooling!** 🏟️⚾
