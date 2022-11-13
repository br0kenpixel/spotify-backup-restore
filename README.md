<p align="center">
  <img align="center" width="500" src="https://github.com/br0kenpixel/spotify-backup-restore/blob/eb16111d7d0596893612f941a882e40b68853f12/img/main_window.png">
</p>
<h1 align="center">🎵 Spotify Backup and Restore Tool 📝</h1>
<p align="center">A tool for backing up your Spotify library!</p>
<p align="center">Check the <a href="https://github.com/br0kenpixel/spotify-backup-restore/wiki">wiki</a> for more info.</p>

## Backups!
With the help of SBRT you can easily back up your Spotify library!
<details>
  <summary>What is backed up?</summary>
  - Liked Songs </br>
  - All your playlists
</details>
<details>
  <summary>Can I choose what to back up?</summary>
  Absolutely! SBRT gives you the ability to choose what to back up and what to restore!
</details>
<details>
  <summary>What format is used for the backup files? Is it custom?</summary>
  The backup files use the <i>.sbt (Spotify Backup Tool)</i> extension. They are nothing more than just simple JSON files. In some cases the backup file may start with a <a href="https://en.wikipedia.org/wiki/Lempel%E2%80%93Ziv%E2%80%93Markov_chain_algorithm">LZMA</a> or <a href="https://en.wikipedia.org/wiki/Gzip">GZIP</a> header. In such cases it means that the file was compressed. The backup tool allows users to compress the backup file.
  <details>
    <summary>Why JSON?</summary>
      JSON syntax is simple and fast to parse. This also allows third-party tools to work with SBRT's backup files easily, no need for a custom parser.
    </details>
  <details>
    <summary>What compression methods are supported?</summary>
    The currently supported compression methods are:</br>
    <ul>
      <li>GZIP</li>
      <ul>
        <li>Fast compression and decompression</li>
      </ul>
      <li>LZMA</li>
      <ul>
        <li>Slow to compress, but decompression is much faster</li>
        <li>Compression ratios are usually much higher than any other compression method</li>
      </ul>
    </ul>
  </details>
  <details>
    <summary>Will there be support for other formats?</summary>
    I may implement support for YAML or XML but for now I think JSON will suffice.
  </details>
</details>
