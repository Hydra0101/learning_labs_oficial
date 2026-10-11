from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0004_classcomment_classlike'),  # <-- Pon el nombre exacto aquí
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE tasks_materia DROP CONSTRAINT IF EXISTS tasks_materia_nombre_887dc5e5_uniq CASCADE;
                DROP INDEX IF EXISTS tasks_materia_nombre_887dc5e5_uniq CASCADE;
            """,
            reverse_sql=migrations.RunSQL.noop
        ),
    ]