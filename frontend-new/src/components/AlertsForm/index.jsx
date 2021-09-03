import React, { useState, useEffect } from 'react';

import { useHistory } from 'react-router-dom';

import { useDispatch, useSelector } from 'react-redux';

import Slack from '../../assets/images/alerts/slack.svg';
import Email from '../../assets/images/alerts/gmail.svg';

import { getAllAlertEmail } from '../../redux/actions';

const AlertsForm = () => {
  const history = useHistory();

  const data = history.location.pathname.split('/');
  const { emailLoading, emailData } = useSelector((state) => {
    return state.alert;
  });
  const dispatch = useDispatch();
  const [webhookUrl, setWebhookUrl] = useState('');
  const [webhookUrlError, setWebhookUrlError] = useState(false);

  const [email, setEmail] = useState({
    smtp: '',
    port: '',
    username: '',
    password: '',
    emailsender: ''
  });
  const [emailError, setEmailError] = useState({
    smtp: false,
    port: false,
    username: false,
    password: false,
    emailsender: false
  });

  useEffect(() => {
    if (emailData && emailData.status === 'success') {
      history.push('/alerts/channelconfiguration');
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [emailData]);

  const alertHandler = () => {
    if (data[2] === 'email') {
      if (email.smtp === '') {
        setEmailError((prev) => {
          return { ...prev, smtp: true };
        });
      }
      if (email.port === '') {
        setEmailError((prev) => {
          return { ...prev, port: true };
        });
      }
      if (email.username === '') {
        setEmailError((prev) => {
          return { ...prev, username: true };
        });
      }
      if (email.password === '') {
        setEmailError((prev) => {
          return { ...prev, password: true };
        });
      }
      if (email.emailsender === '') {
        setEmailError((prev) => {
          return { ...prev, emailsender: true };
        });
      }
      if (
        (email.smtp &&
          email.port &&
          email.username &&
          email.password &&
          email.emailsender) !== ''
      ) {
        const data = {
          config_name: 'email',
          config_settings: {
            server: email.smtp,
            port: email.port,
            username: email.username,
            password: email.password,
            sender_email: email.emailsender
          }
        };
        dispatchGetAllAlertEmail(data);
      }
    } else if (data[2] === 'slack') {
      if (webhookUrl !== '') {
        const slackData = {
          config_name: 'slack',
          config_settings: {
            webhook_url: webhookUrl
          }
        };
        dispatchGetAllAlertEmail(slackData);
      } else {
        setWebhookUrlError(true);
      }
    }
  };

  const dispatchGetAllAlertEmail = (data) => {
    dispatch(getAllAlertEmail(data));
  };

  return (
    <>
      {data[2] === 'slack' ? (
        <>
          <div className="form-group form-title-image">
            <img src={Slack} alt="Slack" />
          </div>
          <div className="form-group">
            <label>Webhook URL *</label>
            <input
              type="text"
              className="form-control"
              placeholder="Enter Webhook URL"
              onChange={(e) => {
                setWebhookUrl(e.target.value);
                setWebhookUrlError(false);
              }}
            />
            {webhookUrlError && (
              <div className="connection__fail">
                <p>Enter Webhook URL</p>
              </div>
            )}
          </div>
        </>
      ) : data[2] === 'email' ? (
        <>
          <div className="form-group form-title-image">
            <img src={Email} alt="Email" />
          </div>
          <div className="form-group">
            <label>SMTP server *</label>
            <input
              type="text"
              className="form-control"
              placeholder="Enter SMTP server"
              onChange={(e) =>
                setEmail((prev) => {
                  return { ...prev, smtp: e.target.value };
                })
              }
            />
            {emailError.smtp === true ? (
              <div className="connection__fail">
                <p>Enter SMTP server</p>
              </div>
            ) : null}
          </div>
          <div className="form-group">
            <label>Port *</label>
            <input
              type="text"
              className="form-control"
              placeholder="Enter Port"
              onChange={(e) =>
                setEmail((prev) => {
                  return { ...prev, port: e.target.value };
                })
              }
            />
            {emailError.port === true ? (
              <div className="connection__fail">
                <p>Enter Port</p>
              </div>
            ) : null}
          </div>
          <div className="form-group">
            <label>Username *</label>
            <input
              type="text"
              className="form-control"
              placeholder="Enter Username"
              onChange={(e) =>
                setEmail((prev) => {
                  return { ...prev, username: e.target.value };
                })
              }
            />
            {emailError.username === true ? (
              <div className="connection__fail">
                <p>Enter username</p>
              </div>
            ) : null}
          </div>
          <div className="form-group">
            <label>Password *</label>
            <input
              type="password"
              className="form-control"
              placeholder="Enter Password"
              onChange={(e) =>
                setEmail((prev) => {
                  return { ...prev, password: e.target.value };
                })
              }
            />
            {emailError.password === true ? (
              <div className="connection__fail">
                <p>Enter password</p>
              </div>
            ) : null}
          </div>
          <div className="form-group">
            <label>Email Sender *</label>
            <input
              type="text"
              className="form-control"
              placeholder="Enter Email"
              onChange={(e) =>
                setEmail((prev) => {
                  return { ...prev, emailsender: e.target.value };
                })
              }
            />
            {emailError.emailsender === true ? (
              <div className="connection__fail">
                <p>Enter Email sender</p>
              </div>
            ) : null}
          </div>
        </>
      ) : null}

      <div className="form-action">
        {/* <Link to="/alerts/channelconfiguration">
          <button className="btn white-button btn-spacing">
            <span>Cancel</span>
          </button>
        </Link> */}
        <button
          className={
            emailLoading ? 'btn black-button btn-loading' : 'btn black-button'
          }
          onClick={() => alertHandler()}>
          <div className="btn-spinner">
            <div className="spinner-border" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
            <span>Loading...</span>
          </div>
          <div className="btn-content">
            <span>Save</span>
          </div>
        </button>
      </div>
    </>
  );
};

export default AlertsForm;
