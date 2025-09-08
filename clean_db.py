from app import db, app
from app.models import Status

def clean_database():
    with app.app_context():
        # Delete all entries for LAB01 and LAB02
        Status.query.filter(Status.domain_name.in_(['ENG-RH227-LAB01', 'ENG-RH227-LAB02'])).delete(synchronize_session=False)
        db.session.commit()
        print("Removed LAB01 and LAB02 entries from database")

if __name__ == '__main__':
    clean_database() 