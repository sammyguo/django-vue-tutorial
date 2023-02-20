# Generated by Django 4.1.1 on 2023-02-16 08:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0003_category_alter_article_options_article_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=30)),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.AddField(
            model_name='article',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='articles', to='article.tag'),
        ),
    ]