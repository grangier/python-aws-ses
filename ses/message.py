# -*- coding: utf-8 -

from email.Utils import formatdate
from email import Charset
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

Charset.add_charset('utf-8', Charset.SHORTEST, None, 'utf-8')

class SimpleEmailServiceMessageBase(object):
    """
    
    """
    def __init__(self, subject='', body='', from_email=None, to=None, bcc=None, headers=None, cc=None):
        """
        
        """
        # check subject
        assert subject, '"subject" cannot be empty'
        assert body, '"body" cannot be empty'
        
        if to:
            assert not isinstance(to, basestring), '"to" argument must be a list or tuple'
            self.to = list(to)
        else:
            self.to = []
        if cc:
            assert not isinstance(cc, basestring), '"cc" argument must be a list or tuple'
            self.cc = list(cc)
        else:
            self.cc = []
        if bcc:
            assert not isinstance(bcc, basestring), '"bcc" argument must be a list or tuple'
            self.bcc = list(bcc)
        else:
            self.bcc = []
        
        self.from_email = from_email
        self.subject = subject
        self.body = body
        self.extra_headers = headers or {}
        
    
    def _create_msg_headers(self, msg):
        msg['Subject'] = self.subject
        msg['From'] = self.extra_headers.get('From', self.from_email)
        msg['To'] = ', '.join(self.to)
        if self.cc:
            msg['Cc'] = ', '.join(self.cc)
        
        # Email header names are case-insensitive (RFC 2045), so we have to
        # accommodate that when doing comparisons.
        header_names = [key.lower() for key in self.extra_headers]
        if 'date' not in header_names:
            msg['Date'] = formatdate()
        #if 'message-id' not in header_names:
        #    msg['Message-ID'] = make_msgid()
        for name, value in self.extra_headers.items():
            if name.lower() == 'from':  # From is already handled
                continue
            msg[name] = value
        return msg
    
    def recipients(self):
        """
        Returns a list of all recipients of the email (includes direct
        addressees as well as Cc and Bcc entries).
        """
        return self.to + self.cc + self.bcc
    
    
    def send(self, fail_silently=False):
        ses = SimpleEmailService()
        ses.SendEmail(self)
    


class SimpleEmailServiceMessage(SimpleEmailServiceMessageBase):
    """
    
    """
    def message(self):
        msg = MIMEText('self.body', 'plain', 'utf-8')
        return self._create_msg_headers(msg)
    
    
    


class SimpleEmailServiceMessageAlternative(SimpleEmailServiceMessage):
    """
    """
    def __init__(self, subject='', body='', from_email=None, to=None, bcc=None, headers=None, alternatives=None, cc=None):
        """
        """
        super(SimpleEmailServiceMessageAlternative, self).__init__(subject, body, from_email, to, bcc, headers, cc)
        self.alternatives = alternatives or []
        
    
    def attach_alternative(self, content, mimetype):
        """Attach an alternative content representation."""
        assert content is not None
        assert mimetype is not "text/html"
        self.alternatives.append((content, mimetype))
        
    
    
    def message(self):
        msg = MIMEMultipart('alternative')
        part = MIMEText(self.body, 'plain', 'utf-8')
        msg.attach(part)
        for alt in self.alternatives:
            part = MIMEText(alt[0], alt[1].split('/')[1], 'utf-8')
            msg.attach(part)
        return self._create_msg_headers(msg)
    

