import { useEffect, useMemo, useState } from 'react';
import styled from 'styled-components';
import SamplePreview from './SamplePreview';
import {
  DRIVER_PATH,
  VENDOR_PACKS,
  downloadJt,
  loadBundledSamples,
  loadVendorPack,
  readJt,
  sendCommandFor,
} from './helpers/samples';

const Page = styled.div`
  width: 100%;
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 24px 64px;
  text-align: left;
`;

const Lede = styled.p`
  font-size: 14px;
  line-height: 1.7;
  color: #9a9ab0;
  margin: 0 0 20px;
  max-width: 720px;
`;

const HowTo = styled.details`
  margin-bottom: 24px;
  padding: 14px 18px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;

  summary {
    cursor: pointer;
    font-size: 13px;
    font-weight: 600;
    color: #c0c0d0;
    letter-spacing: 0.5px;
  }

  ol {
    margin: 14px 0 0;
    padding-left: 20px;
    font-size: 13px;
    line-height: 1.8;
    color: #9a9ab0;
  }

  code {
    padding: 1px 5px;
    background: rgba(0, 0, 0, 0.35);
    border-radius: 4px;
    font-size: 12px;
    color: #7ce0c0;
  }
`;

const Controls = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 20px;
`;

const Tab = styled.button`
  padding: 8px 16px;
  background: ${({ $active }) =>
    $active
      ? 'linear-gradient(135deg, #7a5cff 0%, #5c6cff 100%)'
      : 'rgba(255, 255, 255, 0.06)'};
  color: ${({ $active }) => ($active ? '#fff' : '#a0a0b8')};
  border: 1px solid
    ${({ $active }) => ($active ? 'transparent' : 'rgba(255,255,255,0.12)')};
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;

  &:hover {
    color: #fff;
  }
`;

const Search = styled.input`
  flex: 1;
  min-width: 200px;
  padding: 9px 14px;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 999px;
  color: #e0e0ea;
  font-size: 13px;

  &::placeholder {
    color: #6a6a80;
  }

  &:focus {
    outline: none;
    border-color: rgba(122, 92, 255, 0.6);
  }
`;

const Count = styled.span`
  font-size: 12px;
  color: #7a7a90;
`;

const CardGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
`;

const Card = styled.div`
  padding: 14px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  transition: border-color 0.15s ease;

  &:hover {
    border-color: rgba(122, 92, 255, 0.4);
  }
`;

const CardName = styled.div`
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 10px;
  margin: 12px 0 2px;
  font-size: 13px;
  font-weight: 600;
  color: #e0e0ea;
  word-break: break-word;
`;

const Meta = styled.div`
  font-size: 11px;
  color: #7a7a90;
  margin-bottom: 12px;
`;

const Badge = styled.span`
  flex-shrink: 0;
  padding: 2px 8px;
  background: rgba(122, 92, 255, 0.15);
  border-radius: 999px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.5px;
  color: #b0a0ff;
  text-transform: uppercase;
`;

const CardActions = styled.div`
  display: flex;
  gap: 8px;
`;

const SmallButton = styled.button`
  flex: 1;
  padding: 8px 10px;
  background: ${({ $primary }) =>
    $primary
      ? 'linear-gradient(135deg, #7a5cff 0%, #5c6cff 100%)'
      : 'rgba(255,255,255,0.08)'};
  color: ${({ $primary }) => ($primary ? '#fff' : '#c0c0d0')};
  border: ${({ $primary }) =>
    $primary ? 'none' : '1px solid rgba(255,255,255,0.12)'};
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;

  &:hover {
    color: #fff;
    ${({ $primary }) => !$primary && 'background: rgba(255,255,255,0.14);'}
  }
`;

const CommandBox = styled.code`
  display: block;
  margin-top: 10px;
  padding: 8px 10px;
  background: rgba(0, 0, 0, 0.4);
  border-radius: 6px;
  font-family: 'SFMono-Regular', Menlo, Consolas, monospace;
  font-size: 10.5px;
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

const Status = styled.p`
  font-size: 13px;
  color: #8a8aa0;
  padding: 24px 0;
`;

const SampleCard = ({ sample }) => {
  const [hovered, setHovered] = useState(false);
  const [copied, setCopied] = useState(false);
  const [downloaded, setDownloaded] = useState(false);

  const decoded = useMemo(() => {
    try {
      return readJt(sample.jt);
    } catch {
      return null;
    }
  }, [sample]);

  if (!decoded) {
    return (
      <Card>
        <CardName>{sample.name}</CardName>
        <Meta>Could not be decoded</Meta>
      </Card>
    );
  }

  const command = sendCommandFor(sample);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(command);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch (error) {
      console.warn('Could not copy to clipboard', error);
    }
  };

  const handleDownload = () => {
    downloadJt(sample);
    setDownloaded(true);
  };

  return (
    <Card
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      <SamplePreview
        pixelBytes={decoded.pixelBytes}
        frameNum={decoded.frameNum}
        delays={decoded.delays}
        isHovered={hovered}
      />

      <CardName>
        <span>{sample.name}</span>
        {decoded.frameNum > 1 && <Badge>{decoded.frameNum} frames</Badge>}
      </CardName>
      <Meta>
        {decoded.pixelWidth}×{decoded.pixelHeight}
        {decoded.frameNum > 1 && ` · ${decoded.delays}ms per frame`}
        {sample.localPath && ' · already in the repo'}
      </Meta>

      <CardActions>
        {!sample.localPath && (
          <SmallButton $primary onClick={handleDownload}>
            {downloaded ? 'Downloaded' : 'Download .jt'}
          </SmallButton>
        )}
        <SmallButton onClick={handleCopy}>
          {copied ? 'Copied' : 'Copy send command'}
        </SmallButton>
      </CardActions>

      {(downloaded || sample.localPath) && <CommandBox>{command}</CommandBox>}
    </Card>
  );
};

const SamplesPage = () => {
  const [tab, setTab] = useState('bundled');
  const [query, setQuery] = useState('');
  const [cache, setCache] = useState({});
  const [status, setStatus] = useState('loading');
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    if (cache[tab]) {
      setStatus('ready');
      return () => {
        cancelled = true;
      };
    }

    setStatus('loading');
    setError(null);

    const load =
      tab === 'bundled'
        ? loadBundledSamples()
        : loadVendorPack(VENDOR_PACKS.find((pack) => pack.id === tab));

    load
      .then((samples) => {
        if (cancelled) return;
        setCache((previous) => ({ ...previous, [tab]: samples }));
        setStatus('ready');
      })
      .catch((loadError) => {
        if (cancelled) return;
        setError(loadError.message);
        setStatus('error');
      });

    return () => {
      cancelled = true;
    };
  }, [tab, cache]);

  const samples = cache[tab] ?? [];
  const filtered = useMemo(() => {
    const needle = query.trim().toLowerCase();
    if (!needle) return samples;
    return samples.filter((sample) =>
      sample.name.toLowerCase().includes(needle),
    );
  }, [samples, query]);

  const activePack = VENDOR_PACKS.find((pack) => pack.id === tab);

  return (
    <Page>
      <Lede>
        Every sample bundled with this repo, plus the two vendor packs linked in
        the README. Preview them here, download a <code>.jt</code>, and copy the
        command that pushes it to the panel. Hover an animation to play it.
      </Lede>

      <HowTo>
        <summary>Sending one of these to the sign</summary>
        <ol>
          <li>
            Force-quit the CoolLED1248 app — the sign takes one connection.
          </li>
          <li>
            Download a sample, or use the repo path shown for the bundled ones.
          </li>
          <li>
            Run the sample&apos;s command from a terminal with Bluetooth
            permission (iTerm2 works; Terminal.app does not declare the
            entitlement).
          </li>
        </ol>
        <ol start="4">
          <li>
            Needs the driver checked out at <code>{DRIVER_PATH}</code> with a
            venv holding <code>bleak</code> and <code>pillow</code>.
          </li>
        </ol>
      </HowTo>

      <Controls>
        <Tab $active={tab === 'bundled'} onClick={() => setTab('bundled')}>
          In this repo
        </Tab>
        {VENDOR_PACKS.map((pack) => (
          <Tab
            key={pack.id}
            $active={tab === pack.id}
            onClick={() => setTab(pack.id)}
          >
            {pack.label}
          </Tab>
        ))}
        <Search
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Filter by name…"
        />
        {status === 'ready' && (
          <Count>
            {filtered.length}
            {filtered.length !== samples.length && ` of ${samples.length}`}
          </Count>
        )}
      </Controls>

      {activePack && status === 'ready' && <Lede>{activePack.blurb}</Lede>}

      {status === 'loading' && <Status>Loading samples…</Status>}
      {status === 'error' && <Status>Could not load samples: {error}</Status>}
      {status === 'ready' && filtered.length === 0 && (
        <Status>Nothing matches “{query}”.</Status>
      )}

      {status === 'ready' && (
        <CardGrid>
          {filtered.map((sample) => (
            <SampleCard key={sample.id} sample={sample} />
          ))}
        </CardGrid>
      )}
    </Page>
  );
};

export default SamplesPage;
