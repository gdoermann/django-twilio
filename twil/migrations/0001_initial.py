# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'Sms'
        db.create_table('twil_sms', (
            ('body', self.gf('django.db.models.fields.CharField')(max_length=160)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')()),
            ('price', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=30, decimal_places=3)),
            ('to_number', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('direction', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('account_sid', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('from_number', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('sid', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sent', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('twil', ['Sms'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'Sms'
        db.delete_table('twil_sms')
    
    
    models = {
        'twil.sms': {
            'Meta': {'object_name': 'Sms'},
            'account_sid': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'body': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'direction': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'from_number': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '30', 'decimal_places': '3'}),
            'sent': ('django.db.models.fields.DateTimeField', [], {}),
            'sid': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'to_number': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {})
        }
    }
    
    complete_apps = ['twil']
