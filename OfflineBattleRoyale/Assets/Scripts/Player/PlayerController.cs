using UnityEngine;

[RequireComponent(typeof(CharacterController))]
public class PlayerController : MonoBehaviour
{
  [SerializeField] private float moveSpeed = 6f;
  [SerializeField] private float sprintMultiplier = 1.4f;
  [SerializeField] private float jumpForce = 6f;
  [SerializeField] private float gravity = -20f;
  [SerializeField] private Transform cameraPivot;
  [SerializeField] private Camera playerCamera;
  [SerializeField] private PlayerHealth health;
  [SerializeField] private PlayerInventory inventory;
  [SerializeField] private MobileInput mobileInput;

  private CharacterController characterController;
  private Vector3 velocity;
  private float cameraPitch;
  private bool controlsEnabled = true;

  public Camera PlayerCamera => playerCamera;
  public bool ControlsEnabled => controlsEnabled;

  private void Awake()
  {
    characterController = GetComponent<CharacterController>();

    if (playerCamera == null)
    {
      playerCamera = Camera.main;
    }
  }

  private void Update()
  {
    if (!controlsEnabled || !health.IsAlive)
    {
      return;
    }

    HandleLook();
    HandleMovement();
    HandleCombat();
    HandleHealing();
  }

  public void SetControlsEnabled(bool enabled)
  {
    controlsEnabled = enabled;
  }

  private void HandleLook()
  {
    float lookX = mobileInput != null ? mobileInput.LookInput.x : Input.GetAxis("Mouse X");
    float lookY = mobileInput != null ? mobileInput.LookInput.y : Input.GetAxis("Mouse Y");

    transform.Rotate(Vector3.up * lookX);

    cameraPitch -= lookY;
    cameraPitch = Mathf.Clamp(cameraPitch, -80f, 80f);

    if (cameraPivot != null)
    {
      cameraPivot.localRotation = Quaternion.Euler(cameraPitch, 0f, 0f);
    }
  }

  private void HandleMovement()
  {
    Vector2 moveInput = mobileInput != null ? mobileInput.MoveInput : new Vector2(Input.GetAxis("Horizontal"), Input.GetAxis("Vertical"));
    bool sprint = mobileInput != null ? mobileInput.SprintHeld : Input.GetKey(KeyCode.LeftShift);

    Vector3 move = transform.right * moveInput.x + transform.forward * moveInput.y;
    float speed = moveSpeed * (sprint ? sprintMultiplier : 1f);
    characterController.Move(move * speed * Time.deltaTime);

    if (characterController.isGrounded && velocity.y < 0f)
    {
      velocity.y = -2f;
    }

    bool jump = mobileInput != null ? mobileInput.JumpPressed : Input.GetButtonDown("Jump");
    if (jump && characterController.isGrounded)
    {
      velocity.y = jumpForce;
    }

    velocity.y += gravity * Time.deltaTime;
    characterController.Move(velocity * Time.deltaTime);
  }

  private void HandleCombat()
  {
    bool fire = mobileInput != null ? mobileInput.FireHeld : Input.GetButton("Fire1");
    bool reload = mobileInput != null ? mobileInput.ReloadPressed : Input.GetKeyDown(KeyCode.R);

    if (reload)
    {
      inventory.Weapon.TryReload();
    }

    if (fire)
    {
      inventory.Weapon.TryFire(playerCamera, gameObject);
    }
  }

  private void HandleHealing()
  {
    bool heal = mobileInput != null ? mobileInput.HealPressed : Input.GetKeyDown(KeyCode.H);
    if (heal)
    {
      inventory.TryUseMedkit(health);
    }
  }
}
