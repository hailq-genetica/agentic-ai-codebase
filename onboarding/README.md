# Agentic-AI Onboarding
## Prerequisites: Authentication and access 
### Create a CLASSIC GitHub token
If you do not have a [CLASSIC GitHub token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) yet for your GitHub account, please do so. You can going to:
1. Settings
2. Developer settings
3. Personal access tokens
4. **Tokens (classic)**
5. Generate new token > Generate new token (classic)

Importantly, **the following scopes MUST be enabled on your token**. If you already have a token, please update the token to enable these scopes:
- repo and all associated scopes
- **write:packages** and **read:packages**

Whenever you are prompted for your GitHub password, please provide your token.

### Request READ access to project data
Ask Shreya or Jihye to delegate the following Roles to your Google account of choice for this project to the bucket "agentic_ai_dataset", located in the `vanallenlab` Google Cloud project.
- Storage Legacy Bucket Reader
- Storage Legacy Object Reader

### Anthropic API key
Request an Anthropic API key from Shreya. She will DM you the long string.

### Create a Weights & Biases (wandb) account and key
Create an account on [Weights and Biases](https://wandb.ai/site/) **using your Dana-Farber or Harvard email address**. Rather than using "Sign up with GitHub", "Sign up with Google", or "Sign up with Microsoft", provide an email address and password manually. We recommend using an academic email address because you will be given much more storage. Using the Broad Institute email does not seem to grant this benefit.

Create an API key by navigating to **User Settings** > **API keys** > **New key**. Specify a Name of your choice and click "Create API key". 

**SAVE YOUR API KEY**. 

After you create your account, message your email to Shreya so that she can add you to the lab's organization. After receiving her invitation email, **Specify `vanallenlab-agentic-ai` as your default destination for new runs**.

## Creating and setting up your virtual machine
### Download this repository
This repository can be downloaded through GitHub by either using the website or terminal. To download on the website, navigate to the top of this page, click the green Clone or download button, and select Download ZIP to download this repository in a compressed format. To install using GitHub on terminal, type:
```
git clone https://github.com/vanallenlab/agentic-ai-onboarding.git
cd agentic-ai-onboarding
```

### Google Virtual Machine (VM) Setup
First, you should have a lab owned Google Cloud project specific to you. They usually have the naming convention of `vanallenlab-{first letter and then last name}`; for example, `vanallen-sjohri`. If you do not have one, please request one from either Erin Shannon or Brendan Reardon via Slack. **Your Google Cloud project will be referred to ask "vanallen-username" within this README**.

Next, edit the following line of [create_vm.sh](./create_vm.sh) to specify your Google Cloud project.
```
export PROJECT="vanallen-username"
```

With your PROJECT specified, create a VM. To do, you can either:
- Copy and run all code from [create_vm.sh](./create_vm.sh) in your terminal
- Run [create_vm.sh](./create_vm.sh) with `bash create_vm.sh`

### Code and Docker Setup
Once your VM is created, log into it:
```
gcloud compute ssh username@agentic-vm --zone "us-central1-a" --project "vanallen-username"
```

Download this repository, set up the VM, and exit the VM to save changes:
```
git clone https://github.com/vanallenlab/agentic-ai-onboarding.git
cd agentic-ai-onboarding
bash install_docker_on_vm.sh
exit
```

Re-log back into the VM:
```
gcloud compute ssh username@agentic-vm --zone "us-central1-a" --project "vanallen-username"
```

By default, Google Cloud VMs will log you into a service account. Log in with your Google Cloud:
```
gcloud auth login
```

With your Anthropic API key from Shreya, add it to your bash rc. Replace `KEY` with the string that Shreya provided you as an API key.
```
echo 'export ANTHROPIC_API_KEY="KEY"' >> ~/.bashrc
source ~/.bashrc
```

For example:
```
echo 'export ANTHROPIC_API_KEY="sk-ant-api03-abcdef"' >> ~/.bashrc
source ~/.bashrc
```

Log into Docker using your GitHub credentials. As before, provide your CLASSIC token when prompted for your password
```
docker login ghcr.io
```

Once authenticated, rerun docker login to ensure that you have successfully been logged in:
```
docker login ghcr.io
```
Sometimes it doesn't work in one shot; you should re-start your VM and then try the login step again (make sure you remove the `config` file from ~/.docker before re-trying for best results)

Setup code:
```
git clone https://github.com/vanallenlab/agentic-ai-codebase.git
cd agentic-ai-codebase/data/
```

Download the dataset for your specific group:
```
# Epimenta et al.
gcloud storage cp -r gs://agentic_ai_dataset/pilot_datasets/epimenta_liposarcoma/ .

# Yates et al.
gcloud storage cp -r gs://agentic_ai_dataset/pilot_datasets/jyates_eac/ .

# Fu et al.
gcloud storage cp -r gs://agentic_ai_dataset/pilot_datasets/jfu_brca/ .
```

Setup docker:
```
cd ..
chmod -R 777 .
docker pull ghcr.io/vanallenlab/agentic-sc-runtime:v2
```
