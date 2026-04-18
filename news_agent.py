import anthropic
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date

def fetch_news():
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{
            "role": "user",
            "content": (
                f"Today is {date.today()}. Search the web and find the top 20 most important "
                "news stories from today across categories: world, tech, business, science, and health. "
                "Format your response as clean HTML with: "
                "1) A bold headline for each story "
                "2) A 2-sentence summary "
                "3) The news source name "
                "Use <h2> for category headers, <h3> for headlines, <p> for summaries, "
                "and wrap each story in a <div style='margin-bottom:20px'>. "
                "Make it readable and professional."
            )
        }]
    )

    # Extract the text from the final response
    for block in reversed(response.content):
        if hasattr(block, "text"):
            return block.text

    return "<p>Could not fetch news today.</p>"


def send_email(html_content):
    sender = os.environ["GMAIL_ADDRESS"]
    recipient = os.environ["RECIPIENT_EMAIL"]
    password = os.environ["GMAIL_APP_PASSWORD"]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📰 Your Daily Top 20 News — {date.today().strftime('%B %d, %Y')}"
    msg["From"] = sender
    msg["To"] = recipient

    # Wrap in a clean email layout
    full_html = f"""
    <html><body style="font-family: Arial, sans-serif; max-width: 700px;
      margin: auto; padding: 20px; color: #222;">
      <h1 style="color: #1a1a2e; border-bottom: 2px solid #e63946; padding-bottom: 10px;">
        📰 Daily News Digest — {date.today().strftime('%B %d, %Y')}
      </h1>
      {html_content}
      <hr style="margin-top:40px"/>
      <p style="font-size:12px; color:#999;">
        Powered by Claude AI · Delivered daily at 9 AM IST
      </p>
    </body></html>
    """

    msg.attach(MIMEText(full_html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())

    print(f"✅ Email sent to {recipient}")


if __name__ == "__main__":
    print("Fetching today's news...")
    news = fetch_news()
    print("Sending email...")
    send_email(news)
