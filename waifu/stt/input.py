from .stt import stt

def user_input(holder):
    user_input = input(holder).strip()

    if user_input:
        text = user_input
    else:
        text = stt()
        
    # no text input
    #return stt()
    
    return text