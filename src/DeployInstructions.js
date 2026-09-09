import { useState } from 'react';
import styled from 'styled-components';

const DRIVER_PATH = '~/workspace/coolledx-driver';
const DOWNLOADS_PATH = '~/Downloads';

const Panel = styled.div`
  width: 100%;
  max-width: 900px;
  margin: 0 auto 24px;
  padding: 20px 24px;
  text-align: left;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  backdrop-filter: blur(12px);
`;

const PanelTitle = styled.h2`
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: #c0c0d0;
  margin: 0 0 4px;
`;

const Intro = styled.p`
  font-size: 13px;
  line-height: 1.6;
  color: #9a9ab0;
  margin: 0 0 20px;
`;

const Step = styled.div`
  margin-bottom: 18px;

  &:last-child {
    margin-bottom: 0;
  }
`;

const StepLabel = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: #e0e0ea;
  margin-bottom: 8px;
`;

const StepNumber = styled.span`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  border-radius: 50%;
  background: linear-gradient(135deg, #7a5cff 0%, #5c6cff 100%);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
`;

const StepNote = styled.p`
  font-size: 12px;
  line-height: 1.6;
  color: #8a8aa0;
  margin: 8px 0 0;
`;

const CommandRow = styled.div`
  display: flex;
  align-items: stretch;
  gap: 8px;
`;

const Command = styled.code`
  flex: 1;
  padding: 10px 12px;
  background: rgba(0, 0, 0, 0.35);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  font-family: 'SFMono-Regular', Menlo, Consolas, monospace;
  font-size: 12px;
  line-height: 1.5;
  color: #7ce0c0;
  overflow-x: auto;
  white-space: pre;

  &::-webkit-scrollbar {
    height: 6px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.15);
    border-radius: 3px;
  }
`;

const CopyButton = styled.button`
  flex-shrink: 0;
  padding: 0 14px;
  background: rgba(255, 255, 255, 0.08);
  color: #c0c0d0;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.14);
    color: #fff;
  }
`;

const Callout = styled.p`
  margin: 20px 0 0;
  padding: 12px 14px;
  background: rgba(122, 92, 255, 0.08);
  border-left: 2px solid rgba(122, 92, 255, 0.5);
  border-radius: 6px;
  font-size: 12px;
  line-height: 1.6;
  color: #a0a0b8;
`;

const CommandBlock = ({ command, note }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(command);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch (error) {
      // Clipboard access can be blocked; the command stays selectable by hand.
      console.warn('Could not copy to clipboard', error);
    }
  };

  return (
    <>
      <CommandRow>
        <Command>{command}</Command>
        <CopyButton onClick={handleCopy}>
          {copied ? 'Copied' : 'Copy'}
        </CopyButton>
      </CommandRow>
      {note && <StepNote>{note}</StepNote>}
    </>
  );
};

const DeployInstructions = ({ lastExportedFile }) => {
  // Before the first export we can't know the filename, so show the pattern.
  const jtPath = lastExportedFile
    ? `${DOWNLOADS_PATH}/${lastExportedFile}`
    : `${DOWNLOADS_PATH}/your-export.jt`;

  return (
    <Panel>
      <PanelTitle>Send to the sign</PanelTitle>
      <Intro>
        Pushes a .jt straight to the panel over Bluetooth from this machine — no
        phone and no CoolLED1248 app. Needs the{' '}
        <a
          href="https://github.com/UpDryTwist/coolledx-driver"
          target="_blank"
          rel="noreferrer"
        >
          coolledx-driver
        </a>{' '}
        checkout at <code>{DRIVER_PATH}</code>.
      </Intro>

      <Step>
        <StepLabel>
          <StepNumber>1</StepNumber>
          Quit the phone app
        </StepLabel>
        <StepNote>
          The sign accepts one Bluetooth connection at a time and stops
          advertising while the app holds it, so force-quit CoolLED1248 —
          backgrounding it is not enough.
        </StepNote>
      </Step>

      <Step>
        <StepLabel>
          <StepNumber>2</StepNumber>
          Confirm the sign is visible
        </StepLabel>
        <CommandBlock
          command={`cd ${DRIVER_PATH} && PYTHONPATH=src .venv/bin/python utils/scan.py -t 15`}
          note="Expect: Device: CoolLEDX (…) with Height: 16, Width: 96. There is no pairing step and the sign never appears in macOS Bluetooth settings — it is an unbonded BLE peripheral, so scan.py is the only place it shows up."
        />
      </Step>

      <Step>
        <StepLabel>
          <StepNumber>3</StepNumber>
          Export, then send
        </StepLabel>
        <CommandBlock
          command={`cd ${DRIVER_PATH} && PYTHONPATH=src .venv/bin/python utils/tweak_sign.py -jt ${jtPath}`}
          note={
            lastExportedFile
              ? 'Filled in with the file you just exported.'
              : 'Hit "Export .jt" and this command updates with the real filename.'
          }
        />
      </Step>

      <Callout>
        On macOS, Bluetooth has to be granted to the terminal running the
        command — iTerm2 works, Terminal.app does not declare the entitlement.
        Run it from a terminal directly, not from an editor or IDE task runner,
        or Python is killed with <code>Abort trap: 6</code> before it can scan.
      </Callout>
    </Panel>
  );
};

export default DeployInstructions;
