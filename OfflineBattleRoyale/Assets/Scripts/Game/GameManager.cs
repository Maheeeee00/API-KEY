using System;
using UnityEngine;

public enum MatchPhase
{
  Waiting,
  Plane,
  Dropping,
  Playing,
  Finished
}

public class GameManager : MonoBehaviour
{
  public static GameManager Instance { get; private set; }

  [SerializeField] private int totalPlayers = 50;
  [SerializeField] private PlaneController planeController;
  [SerializeField] private BotSpawnManager botSpawnManager;
  [SerializeField] private ItemSpawner itemSpawner;
  [SerializeField] private PlayerController player;

  private int playersAlive;
  private MatchPhase phase = MatchPhase.Waiting;

  public int PlayersAlive => playersAlive;
  public MatchPhase Phase => phase;

  public event Action<int> OnAliveCountChanged;
  public event Action<bool> OnMatchEnded;

  private void Awake()
  {
    if (Instance != null && Instance != this)
    {
      Destroy(gameObject);
      return;
    }

    Instance = this;
    playersAlive = totalPlayers;
  }

  private void Start()
  {
    StartMatch();
  }

  public void StartMatch()
  {
    playersAlive = totalPlayers;
    OnAliveCountChanged?.Invoke(playersAlive);

    itemSpawner?.SpawnLoot();
    botSpawnManager?.SpawnBots();

    phase = MatchPhase.Plane;
    player?.SetControlsEnabled(false);
    planeController?.BeginFlight(player?.transform);
  }

  public void OnPlayerJumpedFromPlane()
  {
    if (phase != MatchPhase.Plane)
    {
      return;
    }

    phase = MatchPhase.Dropping;
    botSpawnManager?.TriggerBotDrops();
  }

  public void OnPlayerLanded()
  {
    if (phase != MatchPhase.Dropping)
    {
      return;
    }

    phase = MatchPhase.Playing;
    player?.SetControlsEnabled(true);
  }

  public void RegisterElimination(GameObject eliminated, bool wasBot)
  {
    if (phase == MatchPhase.Finished)
    {
      return;
    }

    playersAlive = Mathf.Max(0, playersAlive - 1);
    OnAliveCountChanged?.Invoke(playersAlive);

    if (!wasBot)
    {
      EndMatch(false);
      return;
    }

    if (playersAlive <= 1)
    {
      EndMatch(true);
    }
  }

  private void EndMatch(bool playerWon)
  {
    phase = MatchPhase.Finished;
    OnMatchEnded?.Invoke(playerWon);
    Debug.Log(playerWon ? "Booyah! You won!" : "Game Over!");
  }
}
