# -*- coding: utf-8 -

import restkit
import time
import hmac
import hashlib
import urllib
import binascii
from lxml import objectify


version_info = (0, 0, 1)
__version__ =  ".".join(map(str, version_info))



class SimpleEmailServiceError(Exception):
    """
    SimpleEmailService Exception
    """
    
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        error = objectify.fromstring(self.value['body'])
        msg = "SimpleEmailService Error: Type:%s Code: %s Message:%s Request Id: %s" % \
            (error.Error.Type, error.Error.Code, 
                error.Error.Message, error.RequestId)
        return repr(msg)



class SimpleEmailServiceRequest(object):
    """
    SimpleEmailService Request
    """
    def __init__(self, ses, method):
        self.ses = ses
        self.method = method
        self.parameters = {}
        self.date = time.strftime("%a, %d %b %Y %X GMT", time.gmtime())
        self.headers = {
            'user_agent':'SimpleEmailService/Python',
            'Date': self.date,
            'Host':self.ses.host
        }
        
    
    
    def getSignature(self):
        """Compute the signature"""
        hashed = hmac.new(self.ses.secretKey, self.date, hashlib.sha256)
        return binascii.b2a_base64(hashed.digest())[:-1]
        
    
    
    def setAuth(self):
        auth = 'AWS3-HTTPS AWSAccessKeyId=%s' % self.ses.accessKey;
        auth += ',Algorithm=HmacSHA256,Signature=%s' % self.getSignature();
        self.headers.update({'X-Amzn-Authorization': auth})
    
    
    def setParameter(self, key, value):
        self.parameters.update({key:value})
        
    
    
    def getRequest(self):
        """
        
        """
        query = urllib.urlencode(self.parameters)
        url = 'https://' + self.ses.host + '/?' + query
        req = restkit.request(url, method=self.method, headers=self.headers)
        body = req.body_string()
        return {
            'status': req.status_int,
            'body': body
        }
        
    
    
    def postRequest(self):
        """
        
        """
        url = 'https://' + self.ses.host + '/'
        req = restkit.request(url, method=self.method, \
                    body=self.parameters, headers=self.headers)
        body = req.body_string()
        return {
            'status': req.status_int,
            'body': body
        }
        
    
    
    def response(self):
        self.setAuth()
        if self.method == 'POST':
            return self.postRequest()
        return self.getRequest()
        
    


class SimpleEmailService(object):
    
    def __init__(self, accessKey=None, secretKey=None, 
                    host='email.us-east-1.amazonaws.com'):
        
        assert accessKey, '"accessKey" cannot be empty'
        assert secretKey, '"secretKey" cannot be empty'
        
        self.accessKey = accessKey
        self.secretKey = secretKey
        self.host = host
        
    
    
    def processResponse(self, response):
        status = response.get('status')
        print status
        body = response.get('body')
        if status == 200:
            return objectify.fromstring(body)
        raise SimpleEmailServiceError(response)
        
    
    
    def DeleteVerifiedEmailAddress(self, EmailAddress):
        """
        Deletes the specified email address from the list 
        of verified addresses.
        """
        sesReq = SimpleEmailServiceRequest(self, 'DELETE')
        sesReq.setParameter('Action', 'DeleteVerifiedEmailAddress')
        sesReq.setParameter('EmailAddress', EmailAddress)
        response = self.processResponse(sesReq.response())
        return {
            'RequestId': response.ResponseMetadata.RequestId,
        }
        
    
    
    def GetSendQuota(self):
        """
        Returns the user's current sending limits.
        """
        sesReq = SimpleEmailServiceRequest(self, 'GET')
        sesReq.setParameter('Action', 'GetSendQuota')
        response = self.processResponse(sesReq.response())
        return {
            'Max24HourSend': response.GetSendQuotaResult.Max24HourSend,
            'MaxSendRate': response.GetSendQuotaResult.MaxSendRate,
            'SentLast24Hours': response.GetSendQuotaResult.SentLast24Hours,
            'RequestId': response.ResponseMetadata.RequestId,
        }
        
    
    
    def GetSendStatistics(self):
        """
        Returns the user's sending statistics. 
        The result is a list of data points, 
        representing the last two weeks of sending activity.
        """
        sesReq = SimpleEmailServiceRequest(self, 'GET')
        sesReq.setParameter('Action', 'GetSendStatistics')
        response = self.processResponse(sesReq.response())
        
        # member
        members = [{'DeliveryAttempts': i.DeliveryAttempts,
            'Timestamp': i.Timestamp,
            'Rejects': i.Rejects,
            'Bounces': i.Bounces,
            'Complaints': i.Complaints } for i in \
                response.GetSendStatisticsResult.SendDataPoints.iterchildren()] 
        
        return {
            'GetSendStatisticsResult': members,
            'RequestId': response.ResponseMetadata.RequestId,
        }
    
    
    def ListVerifiedEmailAddresses(self):
        """
        Returns a list containing all of the email addresses 
        that have been verified.
        """
        sesReq = SimpleEmailServiceRequest(self, 'GET')
        sesReq.setParameter('Action', 'ListVerifiedEmailAddresses')
        response = self.processResponse(sesReq.response())
        
        # emails list
        emails = [ i for i in response.ListVerifiedEmailAddressesResult.\
                                    VerifiedEmailAddresses.iterchildren()]
        return {
            'VerifiedEmailAddresses': emails,
            'RequestId': response.ResponseMetadata.RequestId,
        }
    
    
    def SendEmail(self, Message):
        """
        Composes an email message based on input data, and 
        then immediately queues the message for sending.
        """
        sesReq = SimpleEmailServiceRequest(self, 'POST')
        sesReq.setParameter('Action', 'SendEmail')
        
        # to
        for c, to in enumerate(Message.to):
            sesReq.setParameter('Destination.ToAddresses.member.%s' % (c + 1), to)
        # cc
        for c, cc in enumerate(Message.cc):
            sesReq.setParameter('Destination.CcAddresses.member.%s' % (c + 1), cc)
        # bcc
        for c, bcc in enumerate(Message.bcc):
            sesReq.setParameter('Destination.BccAddresses.member.%s' % (c + 1), bcc)
        # replyto
        
        # from 
        sesReq.setParameter('Source', Message.from_email)
        sesReq.setParameter('ReturnPath',  Message.from_email);
        # subject
        sesReq.setParameter('Message.Subject.Data', Message.subject)
        sesReq.setParameter('Message.Subject.Charset', 'utf-8')
        # text body
        sesReq.setParameter('Message.Body.Text.Data', Message.body)
        sesReq.setParameter('Message.Body.Text.Charset', 'utf-8')
        # html body
        if hasattr(Message, 'body_html'):
            sesReq.setParameter('Message.Body.Html.Data', Message.body_html)
            sesReq.setParameter('Message.Body.Html.Charset', 'utf-8')
        
        # send
        response = self.processResponse(sesReq.response())
        return {
            'MessageId': response.SendEmailResult.MessageId,
            'RequestId': response.ResponseMetadata.RequestId,
        }
        
    
    
    def SendRawEmail(self, from_email, recipients, message_string):
        """
        Sends an email message, with header and content specified by the client. 
        The SendRawEmail action is useful for sending multipart MIME emails. 
        The raw text of the message must comply with Internet email standards; 
        otherwise, the message cannot be sent.
        """
        sesReq = SimpleEmailServiceRequest(self, 'POST')
        sesReq.setParameter('Action', 'SendRawEmail')
        sesReq.setParameter('Source', from_email)
        sesReq.setParameter('RawMessage.Data', binascii.b2a_base64(message_string)[:-1])
        for c, i in enumerate(recipients):
            sesReq.setParameter('Destinations.member.%s' % (c+1), i)
        
        #r = sesReq.response()
        #print r
        response = self.processResponse(sesReq.response())
        return {
            'MessageId': response.SendRawEmailResult.MessageId,
            'RequestId': response.ResponseMetadata.RequestId,
        }
        
    
    
    def VerifyEmailAddress(self, EmailAddress):
        """
        Verifies an email address. 
        This action causes a confirmation email message 
        to be sent to the specified address.
        """
        sesReq = SimpleEmailServiceRequest(self, 'GET')
        sesReq.setParameter('Action', 'VerifyEmailAddress')
        sesReq.setParameter('EmailAddress', EmailAddress)
        response = self.processResponse(sesReq.response())
        return {
            'RequestId': response.ResponseMetadata.RequestId,
        }
        
    


