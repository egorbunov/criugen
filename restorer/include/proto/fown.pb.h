// Generated by the protocol buffer compiler.  DO NOT EDIT!
// source: fown.proto

#ifndef PROTOBUF_fown_2eproto__INCLUDED
#define PROTOBUF_fown_2eproto__INCLUDED

#include <string>

#include <google/protobuf/stubs/common.h>

#if GOOGLE_PROTOBUF_VERSION < 2006000
#error This file was generated by a newer version of protoc which is
#error incompatible with your Protocol Buffer headers.  Please update
#error your headers.
#endif
#if 2006001 < GOOGLE_PROTOBUF_MIN_PROTOC_VERSION
#error This file was generated by an older version of protoc which is
#error incompatible with your Protocol Buffer headers.  Please
#error regenerate this file with a newer version of protoc.
#endif

#include <google/protobuf/generated_message_util.h>
#include <google/protobuf/message.h>
#include <google/protobuf/repeated_field.h>
#include <google/protobuf/extension_set.h>
#include <google/protobuf/unknown_field_set.h>
// @@protoc_insertion_point(includes)

// Internal implementation detail -- do not call these.
void  protobuf_AddDesc_fown_2eproto();
void protobuf_AssignDesc_fown_2eproto();
void protobuf_ShutdownFile_fown_2eproto();

class fown_entry;

// ===================================================================

class fown_entry : public ::google::protobuf::Message {
 public:
  fown_entry();
  virtual ~fown_entry();

  fown_entry(const fown_entry& from);

  inline fown_entry& operator=(const fown_entry& from) {
    CopyFrom(from);
    return *this;
  }

  inline const ::google::protobuf::UnknownFieldSet& unknown_fields() const {
    return _unknown_fields_;
  }

  inline ::google::protobuf::UnknownFieldSet* mutable_unknown_fields() {
    return &_unknown_fields_;
  }

  static const ::google::protobuf::Descriptor* descriptor();
  static const fown_entry& default_instance();

  void Swap(fown_entry* other);

  // implements Message ----------------------------------------------

  fown_entry* New() const;
  void CopyFrom(const ::google::protobuf::Message& from);
  void MergeFrom(const ::google::protobuf::Message& from);
  void CopyFrom(const fown_entry& from);
  void MergeFrom(const fown_entry& from);
  void Clear();
  bool IsInitialized() const;

  int ByteSize() const;
  bool MergePartialFromCodedStream(
      ::google::protobuf::io::CodedInputStream* input);
  void SerializeWithCachedSizes(
      ::google::protobuf::io::CodedOutputStream* output) const;
  ::google::protobuf::uint8* SerializeWithCachedSizesToArray(::google::protobuf::uint8* output) const;
  int GetCachedSize() const { return _cached_size_; }
  private:
  void SharedCtor();
  void SharedDtor();
  void SetCachedSize(int size) const;
  public:
  ::google::protobuf::Metadata GetMetadata() const;

  // nested types ----------------------------------------------------

  // accessors -------------------------------------------------------

  // required uint32 uid = 1;
  inline bool has_uid() const;
  inline void clear_uid();
  static const int kUidFieldNumber = 1;
  inline ::google::protobuf::uint32 uid() const;
  inline void set_uid(::google::protobuf::uint32 value);

  // required uint32 euid = 2;
  inline bool has_euid() const;
  inline void clear_euid();
  static const int kEuidFieldNumber = 2;
  inline ::google::protobuf::uint32 euid() const;
  inline void set_euid(::google::protobuf::uint32 value);

  // required uint32 signum = 3;
  inline bool has_signum() const;
  inline void clear_signum();
  static const int kSignumFieldNumber = 3;
  inline ::google::protobuf::uint32 signum() const;
  inline void set_signum(::google::protobuf::uint32 value);

  // required uint32 pid_type = 4;
  inline bool has_pid_type() const;
  inline void clear_pid_type();
  static const int kPidTypeFieldNumber = 4;
  inline ::google::protobuf::uint32 pid_type() const;
  inline void set_pid_type(::google::protobuf::uint32 value);

  // required uint32 pid = 5;
  inline bool has_pid() const;
  inline void clear_pid();
  static const int kPidFieldNumber = 5;
  inline ::google::protobuf::uint32 pid() const;
  inline void set_pid(::google::protobuf::uint32 value);

  // @@protoc_insertion_point(class_scope:fown_entry)
 private:
  inline void set_has_uid();
  inline void clear_has_uid();
  inline void set_has_euid();
  inline void clear_has_euid();
  inline void set_has_signum();
  inline void clear_has_signum();
  inline void set_has_pid_type();
  inline void clear_has_pid_type();
  inline void set_has_pid();
  inline void clear_has_pid();

  ::google::protobuf::UnknownFieldSet _unknown_fields_;

  ::google::protobuf::uint32 _has_bits_[1];
  mutable int _cached_size_;
  ::google::protobuf::uint32 uid_;
  ::google::protobuf::uint32 euid_;
  ::google::protobuf::uint32 signum_;
  ::google::protobuf::uint32 pid_type_;
  ::google::protobuf::uint32 pid_;
  friend void  protobuf_AddDesc_fown_2eproto();
  friend void protobuf_AssignDesc_fown_2eproto();
  friend void protobuf_ShutdownFile_fown_2eproto();

  void InitAsDefaultInstance();
  static fown_entry* default_instance_;
};
// ===================================================================


// ===================================================================

// fown_entry

// required uint32 uid = 1;
inline bool fown_entry::has_uid() const {
  return (_has_bits_[0] & 0x00000001u) != 0;
}
inline void fown_entry::set_has_uid() {
  _has_bits_[0] |= 0x00000001u;
}
inline void fown_entry::clear_has_uid() {
  _has_bits_[0] &= ~0x00000001u;
}
inline void fown_entry::clear_uid() {
  uid_ = 0u;
  clear_has_uid();
}
inline ::google::protobuf::uint32 fown_entry::uid() const {
  // @@protoc_insertion_point(field_get:fown_entry.uid)
  return uid_;
}
inline void fown_entry::set_uid(::google::protobuf::uint32 value) {
  set_has_uid();
  uid_ = value;
  // @@protoc_insertion_point(field_set:fown_entry.uid)
}

// required uint32 euid = 2;
inline bool fown_entry::has_euid() const {
  return (_has_bits_[0] & 0x00000002u) != 0;
}
inline void fown_entry::set_has_euid() {
  _has_bits_[0] |= 0x00000002u;
}
inline void fown_entry::clear_has_euid() {
  _has_bits_[0] &= ~0x00000002u;
}
inline void fown_entry::clear_euid() {
  euid_ = 0u;
  clear_has_euid();
}
inline ::google::protobuf::uint32 fown_entry::euid() const {
  // @@protoc_insertion_point(field_get:fown_entry.euid)
  return euid_;
}
inline void fown_entry::set_euid(::google::protobuf::uint32 value) {
  set_has_euid();
  euid_ = value;
  // @@protoc_insertion_point(field_set:fown_entry.euid)
}

// required uint32 signum = 3;
inline bool fown_entry::has_signum() const {
  return (_has_bits_[0] & 0x00000004u) != 0;
}
inline void fown_entry::set_has_signum() {
  _has_bits_[0] |= 0x00000004u;
}
inline void fown_entry::clear_has_signum() {
  _has_bits_[0] &= ~0x00000004u;
}
inline void fown_entry::clear_signum() {
  signum_ = 0u;
  clear_has_signum();
}
inline ::google::protobuf::uint32 fown_entry::signum() const {
  // @@protoc_insertion_point(field_get:fown_entry.signum)
  return signum_;
}
inline void fown_entry::set_signum(::google::protobuf::uint32 value) {
  set_has_signum();
  signum_ = value;
  // @@protoc_insertion_point(field_set:fown_entry.signum)
}

// required uint32 pid_type = 4;
inline bool fown_entry::has_pid_type() const {
  return (_has_bits_[0] & 0x00000008u) != 0;
}
inline void fown_entry::set_has_pid_type() {
  _has_bits_[0] |= 0x00000008u;
}
inline void fown_entry::clear_has_pid_type() {
  _has_bits_[0] &= ~0x00000008u;
}
inline void fown_entry::clear_pid_type() {
  pid_type_ = 0u;
  clear_has_pid_type();
}
inline ::google::protobuf::uint32 fown_entry::pid_type() const {
  // @@protoc_insertion_point(field_get:fown_entry.pid_type)
  return pid_type_;
}
inline void fown_entry::set_pid_type(::google::protobuf::uint32 value) {
  set_has_pid_type();
  pid_type_ = value;
  // @@protoc_insertion_point(field_set:fown_entry.pid_type)
}

// required uint32 pid = 5;
inline bool fown_entry::has_pid() const {
  return (_has_bits_[0] & 0x00000010u) != 0;
}
inline void fown_entry::set_has_pid() {
  _has_bits_[0] |= 0x00000010u;
}
inline void fown_entry::clear_has_pid() {
  _has_bits_[0] &= ~0x00000010u;
}
inline void fown_entry::clear_pid() {
  pid_ = 0u;
  clear_has_pid();
}
inline ::google::protobuf::uint32 fown_entry::pid() const {
  // @@protoc_insertion_point(field_get:fown_entry.pid)
  return pid_;
}
inline void fown_entry::set_pid(::google::protobuf::uint32 value) {
  set_has_pid();
  pid_ = value;
  // @@protoc_insertion_point(field_set:fown_entry.pid)
}


// @@protoc_insertion_point(namespace_scope)

#ifndef SWIG
namespace google {
namespace protobuf {


}  // namespace google
}  // namespace protobuf
#endif  // SWIG

// @@protoc_insertion_point(global_scope)

#endif  // PROTOBUF_fown_2eproto__INCLUDED
