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
        """
        <ErrorResponse xmlns="http://ses.amazonaws.com/doc/2010-12-01/">
         <Error>
          <Type>Sender</Type>
          <Code>InvalidClientTokenId</Code>
          <Message>The security token included in the request is invalid</Message>
         </Error>
         <RequestId>ad465a80-a058-11e0-9bdd-e31237b6830c</RequestId>
        </ErrorResponse>
        """
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
        
        HTTP Response:
        <DeleteVerifiedEmailAddressResponse xmlns="http://ses.amazonaws.com/doc/2010-12-01/">
          <ResponseMetadata>
            <RequestId>37ff3aef-a056-11e0-a988-819c7f065636</RequestId>
          </ResponseMetadata>
        </DeleteVerifiedEmailAddressResponse>
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
        
        Reponse:
        <GetSendQuotaResponse xmlns="http://ses.amazonaws.com/doc/2010-12-01/">
          <GetSendQuotaResult>
            <SentLast24Hours>0.0</SentLast24Hours>
            <Max24HourSend>1000.0</Max24HourSend>
            <MaxSendRate>1.0</MaxSendRate>
          </GetSendQuotaResult>
          <ResponseMetadata>
            <RequestId>ba515dd9-a04f-11e0-9268-25f102548904</RequestId>
          </ResponseMetadata>
        </GetSendQuotaResponse>
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
        
        Response:
        <GetSendStatisticsResponse xmlns="http://ses.amazonaws.com/doc/2010-12-01/">
          <GetSendStatisticsResult>
            <SendDataPoints>
              <member>
                <DeliveryAttempts>1</DeliveryAttempts>
                <Timestamp>2011-06-27T01:49:00Z</Timestamp>
                <Rejects>0</Rejects>
                <Bounces>0</Bounces>
                <Complaints>0</Complaints>
              </member>
              <member>
                <DeliveryAttempts>2</DeliveryAttempts>
                <Timestamp>2011-06-27T02:04:00Z</Timestamp>
                <Rejects>0</Rejects>
                <Bounces>0</Bounces>
                <Complaints>0</Complaints>
              </member>
            </SendDataPoints>
          </GetSendStatisticsResult>
          <ResponseMetadata>
            <RequestId>d9263087-a063-11e0-a423-636455206539</RequestId>
          </ResponseMetadata>
        </GetSendStatisticsResponse>
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
        
        HTTP Response:
        <ListVerifiedEmailAddressesResponse xmlns="http://ses.amazonaws.com/doc/2010-12-01/">
          <ListVerifiedEmailAddressesResult>
            <VerifiedEmailAddresses>
              <member>noreply@easy-cv.com</member>
              <member>grangier@recrutae.com</member>
            </VerifiedEmailAddresses>
          </ListVerifiedEmailAddressesResult>
          <ResponseMetadata>
            <RequestId>e0f4799b-a054-11e0-b6c4-0fd9e8385919</RequestId>
          </ResponseMetadata>
        </ListVerifiedEmailAddressesResponse>
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
        if Message.body_html:
            sesReq.setParameter('Message.Body.Html.Data', Message.body_html)
            sesReq.setParameter('Message.Body.Html.Charset', 'utf-8')
        
        # send
        print(sesReq.response())
        
    
    
    def SendRawEmail(self, from_email, recipients, message_string):
        """
        Sends an email message, with header and content specified by the client. 
        The SendRawEmail action is useful for sending multipart MIME emails. 
        The raw text of the message must comply with Internet email standards; 
        otherwise, the message cannot be sent.
        
        <SendRawEmailResponse xmlns="http://ses.amazonaws.com/doc/2010-12-01/">
          <SendRawEmailResult>
            <MessageId>00000130d14c8ada-5ae5714d-2198-47ce-8b92-ba957036f38e-000000</MessageId>
          </SendRawEmailResult>
          <ResponseMetadata>
            <RequestId>d16fc43c-a0c1-11e0-9f24-03d392bd71eb</RequestId>
          </ResponseMetadata>
        </SendRawEmailResponse>
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
        
        Response :
        <VerifyEmailAddressResponse xmlns="http://ses.amazonaws.com/doc/2010-12-01/">
          <ResponseMetadata>
            <RequestId>b0141ccf-a054-11e0-a9bf-a9bdbeaeeeae</RequestId>
          </ResponseMetadata>
        </VerifyEmailAddressResponse>
        """
        sesReq = SimpleEmailServiceRequest(self, 'GET')
        sesReq.setParameter('Action', 'VerifyEmailAddress')
        sesReq.setParameter('EmailAddress', EmailAddress)
        response = self.processResponse(sesReq.response())
        return {
            'RequestId': response.ResponseMetadata.RequestId,
        }
        
    


